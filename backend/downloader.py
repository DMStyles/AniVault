import asyncio
import json
import os
import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import yt_dlp
from bs4 import BeautifulSoup
from database import add_to_library

router = APIRouter()

active_downloads = {}

class DownloadRequest(BaseModel):
    url: str
    title: str
    episode: str
    quality: Optional[str] = "best"
    output_dir: Optional[str] = os.path.expanduser("~/Downloads/AniVault")
    download_id: str
    thumbnail: Optional[str] = ""
    source: Optional[str] = ""

def get_format_selector(quality: str) -> str:
    quality_map = {
        "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "1080p": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]",
        "720p": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
        "480p": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]",
    }
    return quality_map.get(quality, quality_map["best"])

def resolve_anikoto_url(data_ids: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    server_list_url = f"https://anikototv.to/ajax/server/list?servers={data_ids}"
    resp = httpx.get(server_list_url, headers=headers, timeout=15)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch server list: status {resp.status_code}")
    data = resp.json()
    html = data.get("result", "")
    soup = BeautifulSoup(html, "html.parser")
    li = soup.select_one(".servers li[data-link-id]")
    if not li:
        raise Exception("No streaming servers found for this episode.")
    link_id = li.get("data-link-id")
    source_url = f"https://anikototv.to/ajax/server?get={link_id}"
    resp_source = httpx.get(source_url, headers=headers, timeout=15)
    if resp_source.status_code != 200:
        raise Exception(f"Failed to fetch streaming source: status {resp_source.status_code}")
    source_data = resp_source.json()
    final_url = source_data.get("result", {}).get("url")
    if not final_url:
        raise Exception("Failed to extract final streaming URL.")
    return final_url

@router.post("/start")
async def start_download(req: DownloadRequest):
    os.makedirs(req.output_dir, exist_ok=True)
    active_downloads[req.download_id] = {
        "id": req.download_id,
        "title": req.title,
        "episode": req.episode,
        "url": req.url,
        "status": "starting",
        "progress": 0,
        "speed": "",
        "eta": "",
        "output_path": "",
        "thumbnail": req.thumbnail,
        "source": req.source,
    }

    def progress_hook(d):
        dl = active_downloads.get(req.download_id, {})
        if d["status"] == "downloading":
            dl["status"] = "downloading"
            dl["progress"] = float(d.get("_percent_str", "0%").replace("%", "").strip())
            dl["speed"] = d.get("_speed_str", "")
            dl["eta"] = d.get("_eta_str", "")
        elif d["status"] == "finished":
            dl["status"] = "finished"
            dl["progress"] = 100
            file_path = d.get("filename", "")
            dl["output_path"] = file_path
            try:
                # Add to library database on completion
                add_to_library(
                    title=req.title,
                    episode=req.episode,
                    file_path=file_path,
                    thumbnail=req.thumbnail,
                    source=req.source
                )
            except Exception as e:
                print("[Database Error] failed to add to library:", str(e))

    def run_download():
        target_url = req.url
        if target_url.startswith("anikoto:"):
            try:
                data_ids = target_url.split("anikoto:")[1]
                target_url = resolve_anikoto_url(data_ids)
            except Exception as e:
                if req.download_id in active_downloads:
                    active_downloads[req.download_id]["status"] = "error"
                    active_downloads[req.download_id]["error"] = f"Failed to resolve URL: {str(e)}"
                return

        ydl_opts = {
            "format": get_format_selector(req.quality),
            "outtmpl": os.path.join(req.output_dir, f"{req.title} - {req.episode}.%(ext)s"),
            "progress_hooks": [progress_hook],
            "noplaylist": True,
            "quiet": True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([target_url])
        except Exception as e:
            if req.download_id in active_downloads:
                active_downloads[req.download_id]["status"] = "error"
                active_downloads[req.download_id]["error"] = str(e)

    asyncio.get_event_loop().run_in_executor(None, run_download)
    return {"download_id": req.download_id, "status": "started"}

@router.get("/status/{download_id}")
async def get_status(download_id: str):
    return active_downloads.get(download_id, {"error": "Not found"})

@router.get("/all")
async def get_all():
    return list(active_downloads.values())

@router.delete("/{download_id}")
async def cancel_download(download_id: str):
    if download_id in active_downloads:
        active_downloads[download_id]["status"] = "cancelled"
    return {"status": "cancelled"}

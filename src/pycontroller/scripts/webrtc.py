import json
import asyncio
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription

from streamer import VideoOpencvTrack

pcs = set()

video_track = None
data_channel = None
    
async def offer(request):
    global video_track

    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    channel = pc.createDataChannel("anu")

    @channel.on("open")
    def on_open():
        print("data channel has open!")

    @channel.on("message")
    def on_message(message):
        channel.send(message+"received")

    if video_track:
        pc.addTrack(video_track)

    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

def init_video_track(video):
    global video_track
    video_track = VideoOpencvTrack(video)

def start():
    global data_channel

    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_post("/offer", offer)

    web.run_app(app, host="0.0.0.0", port=8090)
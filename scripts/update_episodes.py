import json,re
from pathlib import Path
from yt_dlp import YoutubeDL

URL="https://www.youtube.com/playlist?list=PLsmaUhkCwW3q5q46uc9So2b4D-pZqVZOV"
PREFIX=re.compile(r"^\s*\[전편공개\]\s*먼작귀\s*\(먼가 작고 귀여운 녀석\)\s*")
NUMBER=re.compile(r"(?<!\d)(\d{1,4})\s*화")
def clean(s):
    return re.sub(r"^[-–|:\s]+","",PREFIX.sub("",s or "")).strip()
with YoutubeDL({"extract_flat":"in_playlist","ignoreerrors":True,"quiet":True,"skip_download":True,"playlistend":None}) as ydl:
    data=ydl.extract_info(URL,download=False)
entries=[]
seen_ids=set()
for pos,item in enumerate(data.get("entries") or []):
    if not item: continue
    vid=item.get("id") or ""
    if not re.fullmatch(r"[\w-]{11}",vid) or vid in seen_ids:continue
    seen_ids.add(vid)
    title=clean(item.get("title") or "")
    # The first source item is a one-hour compilation.
    if pos==0:continue
    nums=[int(x) for x in NUMBER.findall(title)]
    episode=nums[0] if len(nums)==1 else None
    if episode is None or episode <= 0: continue\n    if re.search(r"인터뷰|성우|비공개|삭제된|private video|deleted video",title,re.I): continue\n    entries.append({"id":vid,"title":title,"episode":episode,"sourceOrder":pos})
# Keep the first source occurrence for each single episode number.
used=set()
unique=[]
for item in entries:
    ep=item["episode"]
    if ep is not None:
        if ep in used:continue
        used.add(ep)
    unique.append(item)
unique.sort(key=lambda x:(x["episode"] is None,x["episode"] if x["episode"] is not None else x["sourceOrder"],x["sourceOrder"]))
if len(unique)<201:
    raise RuntimeError(f"Only {len(unique)} episodes found; refusing to overwrite existing catalog")
Path("episodes.json").write_text(json.dumps(unique,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"Saved {len(unique)} videos; max episode {max(used) if used else 'unknown'}")

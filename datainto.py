import json,os,re,sys,time
from datetime import datetime,timezone
from urllib.parse import urlparse,unquote
import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build

C16=2
C4="internshala_directory_progress.json"
C17=[30,60,120]


def F7(pn):
    if pn<=1:
        return C1
    return f"{C1}page-{pn}/"


C1="https://internshala.com/companies/"
C5=os.environ["GOOGLE_SHEET_ID"]


class Ex(Exception):
    pass


def F6(u,timeout=15):
    le=None
    for at in range(len(C17)+1):
        try:
            rp=requests.get(u,headers=C7,timeout=timeout)
            if rp.status_code==404:
                print(f"  [warn] Page not found (404): {u}",file=sys.stderr)
                return None
            rp.raise_for_status()
            return rp.text
        except Exception as e:
            le=e
            if at<len(C17):
                ws=C17[at]
                print(f"  [retry] Could not load {u}: {e}. Waiting {ws}s and trying again...",file=sys.stderr)
                time.sleep(ws)
    raise Ex(f"Still failing after {len(C17)+1} tries: {u} ({le})")


C7={"User-Agent":("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")}
C13=re.compile(r"^(?:https?://internshala\.com)?/company/([a-zA-Z0-9-]+)/?$")


def F4():
    fr={"page":1,"index":0,"last_page":60,"round":1,"code_version":C16}
    if os.path.exists(C4):
        try:
            with open(C4,"r",encoding="utf-8") as f:
                dt=json.load(f)
            if int(dt.get("code_version",1))<C16:
                print("Progress was saved by an older version that could skip companies. Starting again from page 1 once to collect them.")
                fr["last_page"]=int(dt.get("last_page",60))
                return fr
            return {"page":int(dt.get("page",1)),"index":int(dt.get("index",0)),"last_page":int(dt.get("last_page",60)),"round":int(dt.get("round",1)),"code_version":C16}
        except Exception:
            pass
    return fr


C14=re.compile(r"/companies/page-(\d+)/?")
C6=os.environ.get("GOOGLE_SHEET_TAB_NAME","Sheet1")


def F8(pn):
    u=F7(pn)
    print(f"Fetching directory page {pn}: {u}")
    h=F6(u)
    if not h:
        return [],None
    sp=BeautifulSoup(h,"html.parser")
    cu=[]
    hp=None
    for a in sp.find_all("a",href=True):
        hr=a["href"].split("?")[0].strip()
        mt=C13.match(hr)
        if mt:
            cu.append(f"https://internshala.com/company/{mt.group(1)}/")
        pm=C14.search(hr)
        if pm:
            nn=int(pm.group(1))
            hp=nn if hp is None else max(hp,nn)
    return list(dict.fromkeys(cu)),hp


C15=["https://www.googleapis.com/auth/spreadsheets"]


def F1():
    ci=json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    cr=service_account.Credentials.from_service_account_info(ci,scopes=C15)
    return build("sheets","v4",credentials=cr)


C12=("internshala","facebook.com","linkedin.com","twitter.com","x.com","instagram.com","youtube.com","google.com","apple.com","wa.me","whatsapp.com","t.me","play.google","apps.apple","bit.ly")


def F9(hr,lt):
    if not hr.startswith("http"):
        return False
    dm=urlparse(hr).netloc.lower().replace("www.","")
    if not dm or any(b in dm for b in C12):
        return False
    tx=lt.lower().replace("https://","").replace("http://","").replace("www.","").strip("/ ")
    return bool(tx) and (dm in tx or tx in dm or tx=="website")


def F2(sv):
    ma=5
    for at in range(1,ma+1):
        try:
            rs=sv.spreadsheets().values().get(spreadsheetId=C5,range=f"{C6}!A2:A").execute()
            rw=rs.get("values",[])
            return set(r[0].strip().lower() for r in rw if r)
        except Exception as e:
            if at==ma:
                raise
            ws=5*at
            print(f"  [retry] reading sheet failed (attempt {at}/{ma}): {e}. Retrying in {ws}s...",file=sys.stderr)
            time.sleep(ws)


C9=re.compile(r"[a-z0-9_.+-]+@[a-z0-9-]+(\.[a-z0-9-]+)+")
C2=2


def F10(tx):
    tx=(tx or "").strip()
    for s in (" | "," :: ",": "," - "," – "):
        if s in tx:
            tx=tx.split(s)[0].strip()
    if not tx or "internshala" in tx.lower():
        return None
    return tx


def F3(sv,rv):
    bo={"values":[rv]}
    ma=5
    for at in range(1,ma+1):
        try:
            sv.spreadsheets().values().append(spreadsheetId=C5,range=f"{C6}!A1",valueInputOption="USER_ENTERED",insertDataOption="INSERT_ROWS",body=bo).execute()
            return
        except Exception as e:
            if at==ma:
                raise
            ws=5*at
            print(f"  [retry] writing row failed (attempt {at}/{ma}): {e}. Retrying in {ws}s...",file=sys.stderr)
            time.sleep(ws)


C10=("sentry.io","wixpress.com","example.com","godaddy.com","yourdomain.com","domain.com","internshala.com")


def F11(pu):
    mt=C13.match(pu.replace("https://internshala.com",""))
    if not mt:
        return None
    sl=re.sub(r"-\d+$","",mt.group(1))
    wd=[w for w in sl.split("-") if w]
    return " ".join(w.capitalize() for w in wd) or None


C8=re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def F13(xs):
    se=set()
    cl=[]
    for em in xs:
        el=unquote(em).lower().strip().strip(".,;:'\"<>()[] ")
        if not C9.fullmatch(el):
            continue
        if el in se:
            continue
        if any(b in el for b in C10):
            continue
        if el.endswith((".png",".jpg",".jpeg",".gif",".svg",".webp")):
            continue
        se.add(el)
        cl.append(el)
    return cl


C11=["/contact","/contact-us","/contactus","/about","/about-us"]


def F5(pr):
    pr["updated_at"]=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(C4,"w",encoding="utf-8") as f:
        json.dump(pr,f,indent=2)


def F12(pu):
    h=F6(pu)
    if not h:
        return None,None,None
    sp=BeautifulSoup(h,"html.parser")
    cn=None
    hd=sp.find("h1")
    if hd:
        cn=hd.get_text(" ",strip=True) or None
    if not cn:
        og=sp.find("meta",attrs={"property":"og:title"})
        if og and og.get("content"):
            cn=F10(og["content"])
    if not cn and sp.title and sp.title.string:
        cn=F10(sp.title.string)
    if not cn:
        cn=F11(pu)
    wu=None
    fi=None
    for a in sp.find_all("a",href=True):
        hr=a["href"].strip()
        if not wu and F9(hr,a.get_text(" ",strip=True)):
            wu=hr
        if not fi and "/internship/detail/" in hr:
            cl=hr.split("?")[0]
            if cl.startswith("/"):
                cl="https://internshala.com"+cl
            fi=cl
        if wu and fi:
            break
    return cn,wu,fi


C3=int(os.environ.get("MAX_RUNTIME_MINUTES","300"))


def F14(wu):
    if not wu:
        return None
    ut=[wu]+[wu.rstrip("/")+p for p in C11]
    for u in ut:
        try:
            rp=requests.get(u,headers=C7,timeout=10)
            if rp.status_code!=200:
                continue
        except Exception:
            continue
        sp=BeautifulSoup(rp.text,"html.parser")
        me=[a["href"].replace("mailto:","").split("?")[0] for a in sp.find_all("a",href=True) if a["href"].startswith("mailto:")]
        te=C8.findall(sp.get_text(" "))
        ca=F13(me+te)
        if ca:
            return ca[0]
        time.sleep(C2)
    return None


def F16(pr,ec,sv,dl,co):
    oot=False
    while not oot:
        pg=pr["page"]
        cu,hp=F8(pg)
        if hp:
            pr["last_page"]=max(hp,pg)
        if not cu:
            if pg>=pr["last_page"]:
                print("Reached the end of the directory. Next run starts again from page 1.")
                pr.update({"page":1,"index":0,"round":pr["round"]+1})
                F5(pr)
                break
            pr.update({"page":pg+1,"index":0})
            F5(pr)
            time.sleep(C2)
            continue
        time.sleep(C2)
        for ix in range(pr["index"],len(cu)):
            if time.time()>dl:
                oot=True
                break
            pu=cu[ix]
            print(f"[page {pg}, {ix + 1}/{len(cu)}] {pu}")
            cn,wu,iu=F12(pu)
            time.sleep(C2)
            if not cn:
                print("  [skip] Page loaded but no company name on it.")
            elif cn.strip().lower() in ec:
                print(f"  [skip] Already in sheet: '{cn}'")
                co["skipped"]+=1
            else:
                ef=F14(wu) if wu else None
                sa=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                rw=[cn,wu or "N/A",ef or "Not found",iu or "From company directory",sa,pu]
                F3(sv,rw)
                ec.add(cn.strip().lower())
                co["new"]+=1
                print(f"  [saved] '{cn}' added to sheet.")
            pr["index"]=ix+1
            F5(pr)
        if oot:
            break
        if pg>=pr["last_page"]:
            print("Finished the last directory page. Next run starts again from page 1.")
            pr.update({"page":1,"index":0,"round":pr["round"]+1})
            F5(pr)
            break
        pr.update({"page":pg+1,"index":0})
        F5(pr)


def F15():
    st=time.time()
    dl=st+C3*60
    sv=F1()
    ec=F2(sv)
    print(f"Sheet already has {len(ec)} companies.")
    pr=F4()
    print(f"Starting at directory page {pr['page']}, position {pr['index']} (round {pr['round']}).")
    co={"new":0,"skipped":0}
    try:
        F16(pr,ec,sv,dl,co)
    except Ex as e:
        print(f"\n[stopped] Internshala is not answering right now: {e}",file=sys.stderr)
        print("Position kept. The next run will continue from the same company.",file=sys.stderr)
        F5(pr)
    nc=co["new"]
    sk=co["skipped"]
    mn=round((time.time()-st)/60,1)
    print(f"\nDone in {mn} min. Added {nc} new companies, skipped {sk} already in the sheet.")
    print(f"Next run starts at page {pr['page']}, position {pr['index']}.")


if __name__=="__main__":
    F15()

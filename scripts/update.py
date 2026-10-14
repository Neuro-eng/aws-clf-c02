import json, re, datetime, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED = "https://aws.amazon.com/about-aws/whats-new/recent/feed/"
ORDER = ["Security", "Billing", "Cloud Concepts", "Technology"]
KW = {
 "Security": ["guardduty","inspector","macie","shield","waf","kms","iam","security hub","config","cloudtrail","secrets manager","cognito","artifact","identity center","detective","key management"],
 "Billing": ["cost explorer","budgets","pricing","savings plans","billing","free tier","trusted advisor","cost optimization","reserved instances","support plan"],
 "Cloud Concepts": ["region","regions","availability zone","well-architected","sovereign","local zone","sustainability"],
 "Technology": ["ec2","lambda","s3","ebs","efs","rds","aurora","dynamodb","elasticache","redshift","vpc","cloudfront","route 53","direct connect","bedrock","sagemaker","athena","eks","ecs","fargate","cloudformation","sqs","sns","fsx","glue","kinesis","api gateway","elastic load balancing"],
}
PER_DOMAIN = 5

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "clf-c02-study-page/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def classify(title):
    t = title.lower()
    for d in ORDER:
        for k in KW[d]:
            if re.search(r"\b" + re.escape(k) + r"\b", t):
                return d
    return None

def parse(xml_bytes):
    out = []
    for it in ET.fromstring(xml_bytes).iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        try:
            dt = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
        except Exception:
            dt = ""
        d = classify(title)
        if title and link.startswith("https://") and d:
            out.append({"title": title, "link": link, "date": dt, "domain": d})
    return out

def main():
    items = parse(fetch(FEED))
    items.sort(key=lambda i: i["date"], reverse=True)
    keep, count = [], {}
    for i in items:
        if count.get(i["domain"], 0) < PER_DOMAIN:
            keep.append(i)
            count[i["domain"]] = count.get(i["domain"], 0) + 1
    data = {"updated": datetime.datetime.utcnow().date().isoformat(), "items": keep}
    with open("updates.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    print(len(keep), "items written")

if __name__ == "__main__":
    main()

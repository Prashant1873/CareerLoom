import asyncio
import json
import httpx

# Candidate list of Indian unicorns, tech firms & startups with candidate slugs
CANDIDATES = [
    # (Company Name, Slug, Domain)
    ("CRED", "cred", "Fintech"),
    ("Meesho", "meesho", "Ecommerce"),
    ("Groww", "groww", "Fintech / WealthTech"),
    ("InMobi", "inmobi", "AdTech / AI"),
    ("Glance", "glance", "AI / Consumer Tech"),
    ("Freshworks", "freshworks", "Enterprise SaaS"),
    ("Slice", "slice", "Fintech / Cards"),
    ("Razorpay", "razorpay", "Fintech / Payments"),
    ("Razorpay", "razorpaysoftware", "Fintech / Payments"),
    ("Swiggy", "swiggy", "Food Delivery / Tech"),
    ("Zomato", "zomato", "Food Delivery / Tech"),
    ("Blinkit", "blinkit", "Quick Commerce"),
    ("Zepto", "zepto", "Quick Commerce"),
    ("Zepto", "zeptonow", "Quick Commerce"),
    ("Flipkart", "flipkart", "Ecommerce / Tech"),
    ("PhonePe", "phonepe", "Fintech / UPI"),
    ("Paytm", "paytm", "Fintech"),
    ("One97", "one97", "Fintech"),
    ("Postman", "postman", "DevTools / API"),
    ("BrowserStack", "browserstack", "DevTools / Testing"),
    ("Hasura", "hasura", "Database / DevTools"),
    ("Urban Company", "urbancompany", "Home Services / Tech"),
    ("UrbanClap", "urbanclap", "Home Services / Tech"),
    ("Dream11", "dream11", "Gaming / Tech"),
    ("Dream Sports", "dreamsports", "Gaming / SportsTech"),
    ("Nykaa", "nykaa", "Beauty / Ecommerce"),
    ("Delhivery", "delhivery", "Logistics / Tech"),
    ("ShareChat", "sharechat", "Social Media"),
    ("Cars24", "cars24", "Automotive / Tech"),
    ("Spinny", "spinny", "Automotive / Tech"),
    ("CarDekho", "cardekho", "Automotive / Tech"),
    ("Rapido", "rapido", "Mobility / Rideshare"),
    ("BluSmart", "blusmart", "EV Mobility"),
    ("BluSmart", "blusmartmobility", "EV Mobility"),
    ("Ather Energy", "atherenergy", "EV / Hardware"),
    ("Ola", "ola", "Mobility / EV"),
    ("Ola Cabs", "olacabs", "Mobility"),
    ("Ola Electric", "olaelectric", "EV / Hardware"),
    ("Ultrahuman", "ultrahuman", "HealthTech / Wearables"),
    ("Porter", "porter", "Logistics"),
    ("BlackBuck", "blackbuck", "Logistics"),
    ("Shadowfax", "shadowfax", "Logistics"),
    ("Shiprocket", "shiprocket", "Logistics / SaaS"),
    ("Moglix", "moglix", "B2B Ecommerce"),
    ("Infra.Market", "inframarket", "B2B Construction"),
    ("OfBusiness", "ofbusiness", "B2B SME"),
    ("Zetwerk", "zetwerk", "Manufacturing Tech"),
    ("PharmEasy", "pharmeasy", "HealthTech"),
    ("Tata 1mg", "1mg", "HealthTech"),
    ("Tata 1mg", "tata1mg", "HealthTech"),
    ("Cult.fit", "cultfit", "Fitness / Health"),
    ("Cure.fit", "curefit", "Fitness / Health"),
    ("HealthifyMe", "healthifyme", "HealthTech / AI"),
    ("Licious", "licious", "D2C Food"),
    ("Dunzo", "dunzo", "Quick Commerce"),
    ("Khatabook", "khatabook", "Fintech / SMB"),
    ("Darwinbox", "darwinbox", "HR Tech / SaaS"),
    ("Chargebee", "chargebee", "Fintech / Subscription"),
    ("CleverTap", "clevertap", "Customer Engagement / SaaS"),
    ("LeadSquared", "leadsquared", "CRM / SaaS"),
    ("MoEngage", "moengage", "Customer Engagement / SaaS"),
    ("Whatfix", "whatfix", "Digital Adoption / SaaS"),
    ("HackerRank", "hackerrank", "HR Tech / DevTools"),
    ("Unacademy", "unacademy", "EdTech"),
    ("PhysicsWallah", "physicswallah", "EdTech"),
    ("PhysicsWallah", "pw", "EdTech"),
    ("Eruditus", "eruditus", "EdTech"),
    ("UpGrad", "upgrad", "EdTech"),
    ("Sarvam AI", "sarvam", "Generative AI"),
    ("Sarvam AI", "sarvamai", "Generative AI"),
    ("Krutrim", "krutrim", "AI / Foundational Models"),
    ("Yellow.ai", "yellowai", "Conversational AI"),
    ("Yellow.ai", "yellowmessenger", "Conversational AI"),
    ("Haptik", "haptik", "Conversational AI"),
    ("Gupshup", "gupshup", "Conversational Messaging"),
    ("Sprinklr", "sprinklr", "Customer Experience / SaaS"),
    ("Fractal Analytics", "fractal", "AI & Analytics"),
    ("Fractal Analytics", "fractalanalytics", "AI & Analytics"),
    ("Tiger Analytics", "tigeranalytics", "AI & Data Science"),
    ("Mu Sigma", "musigma", "Data Analytics"),
    ("LatentView", "latentview", "Analytics"),
    ("Games24x7", "games24x7", "Gaming"),
    ("MPL", "mpl", "Gaming / Esports"),
    ("WinZO", "winzo", "Gaming"),
    ("WinZO Games", "winzogames", "Gaming"),
    ("Nazara", "nazara", "Gaming"),
    ("CoinDCX", "coindcx", "Crypto / Web3"),
    ("CoinSwitch", "coinswitch", "Crypto / Web3"),
    ("CoinSwitch", "coinswitchkuber", "Crypto / Web3"),
    ("Mudrex", "mudrex", "Crypto / Wealth"),
    ("Jar", "jar", "Fintech / Micro-Savings"),
    ("Jar", "myjar", "Fintech / Micro-Savings"),
    ("INDmoney", "indmoney", "Fintech / WealthTech"),
    ("Smallcase", "smallcase", "Fintech / Investing"),
    ("Kuvera", "kuvera", "Fintech / WealthTech"),
    ("Scripbox", "scripbox", "Fintech / WealthTech"),
    ("Plum Insurance", "plum", "InsurTech / Health"),
    ("Plum Insurance", "plumhq", "InsurTech / Health"),
    ("Turtlemint", "turtlemint", "InsurTech"),
    ("Acko", "acko", "InsurTech"),
    ("Digit Insurance", "godigit", "InsurTech"),
    ("Digit Insurance", "digit", "InsurTech"),
    ("GoKwik", "gokwik", "Ecommerce Tech"),
    ("Simpl", "simpl", "Fintech / BNPL"),
    ("Uni Cards", "unicards", "Fintech / Credit"),
    ("Uni Cards", "uni", "Fintech / Credit"),
    ("OneCard", "onecard", "Fintech / Credit"),
    ("FPL Technologies", "fpl", "Fintech / Credit"),
    ("KredX", "kredx", "Fintech / Supply Chain"),
    ("Lendingkart", "lendingkart", "Fintech / SME"),
    ("Perfios", "perfios", "Fintech / Data"),
    ("Setu", "setu", "Fintech / Open Banking"),
    ("Pine Labs", "pinelabs", "Fintech / Merchant"),
    ("Mswipe", "mswipe", "Fintech / POS"),
    ("Innoviti", "innoviti", "Fintech / Payments"),
    ("Navi", "navi", "Fintech / Lending"),
    ("Jupiter", "jupiter", "Fintech / Neo-Banking"),
    ("Jupiter", "jupiterapp", "Fintech / Neo-Banking"),
    ("Fi Money", "epifi", "Fintech / Neo-Banking"),
    ("Fi Money", "fi", "Fintech / Neo-Banking"),
    ("Dezerv", "dezerv", "WealthTech"),
    ("Stable Money", "stablemoney", "Fintech"),
    ("Wint Wealth", "wintwealth", "Fintech"),
    ("BharatPe", "bharatpe", "Fintech / QR Payments"),
    ("KreditBee", "kreditbee", "Fintech / Lending"),
    ("MoneyView", "moneyview", "Fintech / Lending"),
    ("Faircent", "faircent", "P2P Lending"),
    ("MobiKwik", "mobikwik", "Fintech / Wallet"),
    ("PaisaBazaar", "paisabazaar", "Fintech / Marketplace"),
    ("PolicyBazaar", "policybazaar", "InsurTech"),
    ("Jio", "jio", "Telecom & Cloud"),
    ("Tata Digital", "tatadigital", "Conglomerate / SuperApp"),
    ("Info Edge", "infoedge", "Internet Consumer"),
    ("Naukri", "naukri", "Job Portal / Tech"),
    ("Dailyhunt", "dailyhunt", "Media / News"),
    ("Josh", "josh", "Short Video"),
    ("Kuku FM", "kukufm", "Audio OTT"),
    ("Pocket FM", "pocketfm", "Audio OTT"),
    ("Pratilipi", "pratilipi", "Indian Language Content"),
    ("Stage", "stage", "Dialect OTT"),
    ("Trell", "trell", "Social Commerce"),
    ("Lokal", "lokal", "Hyperlocal News"),
    ("Chingari", "chingari", "Short Video"),
    ("EloElo", "eloelo", "Social Gaming / Live"),
    ("Kapture CX", "kapture", "Customer Support / SaaS"),
    ("Exotel", "exotel", "Cloud Communications"),
    ("Knowlarity", "knowlarity", "Cloud Telephony"),
    ("Amagi", "amagi", "Broadcast Cloud / SaaS"),
    ("Icertis", "icertis", "Enterprise Contract AI"),
    ("Druva", "druva", "Cloud Data Protection"),
    ("HighRadius", "highradius", "Fintech / AI Treasury"),
    ("Zenoti", "zenoti", "Salon & Spa SaaS"),
    ("Mindtickle", "mindtickle", "Sales Enablement SaaS"),
    ("Sirion", "sirion", "AI Contract Lifecycle"),
    ("SirionLabs", "sirionlabs", "AI Contract Lifecycle"),
    ("Postman", "postman", "API Platform"),
    ("LambdaTest", "lambdatest", "QA Testing Cloud"),
    ("Kovai.co", "kovaico", "Enterprise SaaS"),
    ("Signeasy", "signeasy", "eSignature SaaS"),
    ("VWO", "vwo", "A/B Testing / SaaS"),
    ("Wingify", "wingify", "Conversion Optimization"),
    ("Kissflow", "kissflow", "No-code Workflow"),
    ("Zoho", "zoho", "Cloud Software Suite"),
    ("Kayako", "kayako", "Help Desk Software"),
    ("Chargebee", "chargebee", "Subscription Billing"),
    ("Rocketlane", "rocketlane", "Customer Onboarding SaaS"),
    ("Devtron", "devtron", "Kubernetes Management"),
    ("SigNoz", "signoz", "Open Source APM / Observability"),
    ("DhiWise", "dhiwise", "DevTools / Code Generation"),
    ("Peerlist", "peerlist", "Professional Network"),
    ("Cutshort", "cutshort", "Recruitment Tech"),
    ("Instamojo", "instamojo", "D2C Payments & Store"),
    ("Cashfree Payments", "cashfree", "Payment Gateway"),
    ("Zaggle", "zaggle", "Fintech SaaS"),
    ("EnKash", "enkash", "Corporate Cards / Spend"),
    ("Open Financial", "openfinancial", "SME Neo-Bank"),
    ("Open", "open", "SME Neo-Bank"),
    ("BankBazaar", "bankbazaar", "Fintech"),
    ("Rupeek", "rupeek", "Gold Lending"),
    ("Progcap", "progcap", "Corporate Financing"),
    ("Aye Finance", "ayefinance", "MSME Lending"),
    ("Vivriti Capital", "vivriticapital", "Fintech NBFC"),
    ("Yubi", "yubi", "Debt Marketplace"),
    ("CredAvenue", "credavenue", "Debt Platform"),
    ("Avataar", "avataar", "3D / AI Computer Vision"),
    ("Wysa", "wysa", "AI Mental Health"),
    ("Mad Street Den", "madstreetden", "Enterprise AI"),
    ("Vue.ai", "vueai", "Retail AI"),
    ("Arya.ai", "aryaai", "Banking AI"),
    ("CognitiveScale", "cognitivescale", "Cortex AI"),
    ("Entropik Tech", "entropik", "Emotion AI"),
    ("Entropik", "entropiktech", "Emotion AI"),
    ("Detect Technologies", "detecttechnologies", "Industrial AI"),
    ("Staqu", "staqu", "AI Video Analytics"),
    ("AgNext", "agnext", "AgriTech AI"),
    ("DeHaat", "dehaat", "AgriTech"),
    ("Ninjacart", "ninjacart", "Agri Supply Chain"),
    ("WayCool", "waycool", "Food Agri Supply Chain"),
    ("Captain Fresh", "captainfresh", "B2B Seafood Tech"),
    ("Country Delight", "countrydelight", "D2C Dairy / Food"),
    ("MilkBasket", "milkbasket", "Micro-Delivery"),
    ("Otipy", "otipy", "Fresh Produce Commerce"),
    ("Bira 91", "bira91", "Beverages"),
    ("Boat", "boat", "Consumer Tech / Audio"),
    ("Noise", "noise", "Smart Wearables"),
    ("Fire-Boltt", "fireboltt", "Smart Wearables"),
    ("Mamaearth", "mamaearth", "Honasa / Beauty"),
    ("Honasa", "honasa", "Consumer Brands"),
    ("Sugar Cosmetics", "sugarcosmetics", "Beauty Tech"),
    ("Purplle", "purplle", "Beauty Ecommerce"),
    ("MyGlamm", "myglamm", "Good Glamm Group"),
    ("Good Glamm Group", "goodglammgroup", "Beauty D2C"),
    ("Wakefit", "wakefit", "Sleep & Home Tech"),
    ("Pepperfry", "pepperfry", "Furniture Marketplace"),
    ("Urban Ladder", "urbanladder", "Furniture / Home"),
    ("Livspace", "livspace", "Home Interior Tech"),
    ("HomeLane", "homelane", "Interior Tech"),
    ("Square Yards", "squareyards", "PropTech"),
    ("NoBroker", "nobroker", "PropTech"),
    ("Magicbricks", "magicbricks", "Real Estate Tech"),
    ("99acres", "99acres", "Real Estate"),
    ("Housing.com", "housing", "PropTech"),
    ("Loco", "loco", "Game Streaming"),
    ("Rooter", "rooter", "Gaming Content"),
    ("Nodwin Gaming", "nodwin", "Esports"),
    ("Head Digital Works", "headdigital", "A23 Gaming"),
    ("Gameskraft", "gameskraft", "Gaming"),
    ("Simple Viral Games", "simpleviralgames", "Casual Gaming"),
    ("Lenskart", "lenskart", "Eyewear Tech"),
    ("Fashinza", "fashinza", "Apparel Supply Chain"),
    ("Zivame", "zivame", "Intimate Wear"),
    ("Clovia", "clovia", "Apparel"),
    ("FabAlley", "faballey", "Fashion"),
    ("Bewakoof", "bewakoof", "Apparel"),
    ("Snitch", "snitch", "Fast Fashion D2C"),
    ("The Souled Store", "thesouledstore", "Pop Culture Apparel"),
    ("Hopscotch", "hopscotch", "Kids Fashion"),
    ("FirstCry", "firstcry", "Baby & Kids Ecommerce"),
    ("Classplus", "classplus", "Creator EdTech"),
    ("Teachmint", "teachmint", "Education Infrastructure"),
    ("Cuemath", "cuemath", "Math EdTech"),
    ("Vedantu", "vedantu", "K-12 EdTech"),
    ("Toppr", "toppr", "Learning App"),
    ("Skill-Lync", "skilllync", "Engineering EdTech"),
    ("Scaler", "scaler", "Tech Upskilling"),
    ("InterviewBit", "interviewbit", "Tech Prep"),
    ("Newton School", "newtonschool", "Tech Academy"),
    ("Masai School", "masaischool", "Coding Bootcamp"),
    ("AlmaBetter", "almabetter", "Data Science EdTech"),
    ("GeeksforGeeks", "geeksforgeeks", "EdTech / Prep"),
    ("Lead School", "leadschool", "School EdTech"),
    ("Camp K12", "campk12", "Coding for Kids"),
    ("BrightChamps", "brightchamps", "Next-Gen EdTech"),
    ("Oyo", "oyo", "Hospitality Tech"),
    ("Oyo Rooms", "oyorooms", "Hospitality"),
    ("Treebo", "treebo", "Hotels Tech"),
    ("FabHotels", "fabhotels", "Hospitality"),
    ("MakeMyTrip", "makemytrip", "Online Travel"),
    ("Goibibo", "goibibo", "Travel Tech"),
    ("Yatra", "yatra", "Travel Tech"),
    ("EaseMyTrip", "easemytrip", "Travel Tech"),
    ("Cleartrip", "cleartrip", "Travel"),
    ("Ixigo", "ixigo", "Travel / AI Booking"),
    ("RedBus", "redbus", "Bus Ticketing"),
    ("AbhiBus", "abhibus", "Mobility"),
    ("Chalo", "chalo", "Public Transport Tech"),
    ("Bounce", "bounce", "EV Mobility"),
    ("Yulu", "yulu", "Micro-Mobility / EV"),
    ("Vogo", "vogo", "Scooter Sharing"),
    ("Battery Smart", "batterysmart", "Battery Swapping"),
    ("Sun Mobility", "sunmobility", "Energy Infrastructure"),
    ("Euler Motors", "eulermotors", "EV Commercial"),
    ("Exponent Energy", "exponentenergy", "15-Min Fast Charging"),
    ("Log9 Materials", "log9materials", "Graphene Batteries"),
    ("Simple Energy", "simpleenergy", "EV Two-Wheelers"),
    ("Matter", "matter", "EV Tech"),
    ("River", "river", "EV Mobility"),
    ("Ultraviolette", "ultraviolette", "High-Performance EV"),
    ("Kuku FM", "kukufm", "Audio OTT"),
]

ATS_TYPES = ["greenhouse", "lever", "ashby", "smartrecruiters"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
}

async def probe_endpoint(client: httpx.AsyncClient, sem: asyncio.Semaphore, name: str, slug: str, domain: str, ats: str) -> dict:
    if ats == "greenhouse":
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    elif ats == "ashby":
        url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    elif ats == "lever":
        url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    elif ats == "smartrecruiters":
        url = f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=5"
    else:
        return None

    async with sem:
        try:
            r = await client.get(url, timeout=8.0)
            if r.status_code == 200:
                data = r.json()
                if ats == "greenhouse":
                    jobs = data.get("jobs", [])
                elif ats == "ashby":
                    jobs = data.get("jobs", [])
                elif ats == "lever":
                    jobs = data if isinstance(data, list) else []
                elif ats == "smartrecruiters":
                    jobs = data.get("content", [])
                else:
                    jobs = []

                count = len(jobs)
                if count > 0:
                    print(f"[FOUND] {name:<22} ({slug:<18} on {ats:<12}) -> {count} live listings", flush=True)
                    return {
                        "name": name,
                        "slug": slug,
                        "ats_type": ats,
                        "domain": domain,
                        "job_count": count,
                    }
        except Exception:
            pass
    return None


async def main():
    print(f"Probing {len(CANDIDATES)} candidates across 4 ATS platforms concurrently...", flush=True)
    results = []
    seen_keys = set()
    sem = asyncio.Semaphore(25)

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, limits=httpx.Limits(max_connections=35, max_keepalive_connections=20)) as client:
        tasks = []
        for name, slug, domain in CANDIDATES:
            for ats in ATS_TYPES:
                tasks.append(probe_endpoint(client, sem, name, slug, domain, ats))

        raw_results = await asyncio.gather(*tasks)
        for r in raw_results:
            if r:
                key = f"{r['name']}:{r['slug']}"
                if key not in seen_keys:
                    seen_keys.add(key)
                    results.append(r)

    print(f"\n==========================================", flush=True)
    print(f"Total Discovered: {len(results)} live Indian tech companies with active listings!", flush=True)
    print(f"==========================================", flush=True)

    with open("backend/scripts/discovered_indian.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())

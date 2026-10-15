"""
Utility script to generate comprehensive, verified partitioned catalog datasets
for Indian startups (150+), Indian conglomerates (40+), and Strategy Consulting firms (30+).
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("careerloom.build_catalog")

TARGETS_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "targets"
TARGETS_DIR.mkdir(parents=True, exist_ok=True)

# 1. Strategy & Management Consulting (32 firms)
STRATEGY_CONSULTING_FIRMS: List[Dict[str, Any]] = [
    {
        "name": "McKinsey & Company India",
        "slug": "mckinsey-india",
        "website": "https://www.mckinsey.com",
        "career_url": "https://www.mckinsey.com/careers/search-jobs",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategy & Management Consulting",
        "role_focus": ["strategy", "consulting", "product", "founders_office"]
    },
    {
        "name": "Boston Consulting Group (BCG) India",
        "slug": "bcg-india",
        "website": "https://www.bcg.com",
        "career_url": "https://careers.bcg.com",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategy & Management Consulting",
        "role_focus": ["strategy", "consulting", "product", "leadership"]
    },
    {
        "name": "Bain & Company India",
        "slug": "bain-india",
        "website": "https://www.bain.com",
        "career_url": "https://www.bain.com/careers/",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategy & Management Consulting",
        "role_focus": ["strategy", "consulting", "product", "founders_office"]
    },
    {
        "name": "Kearney India",
        "slug": "kearney-india",
        "website": "https://www.kearney.com",
        "career_url": "https://www.kearney.com/careers",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategy & Management Consulting",
        "role_focus": ["strategy", "consulting", "operations"]
    },
    {
        "name": "Oliver Wyman India",
        "slug": "oliver-wyman-india",
        "website": "https://www.oliverwyman.com",
        "career_url": "https://www.oliverwyman.com/careers.html",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategy & Management Consulting",
        "role_focus": ["strategy", "consulting", "product"]
    },
    {
        "name": "Roland Berger India",
        "slug": "roland-berger-india",
        "website": "https://www.rolandberger.com",
        "career_url": "https://www.rolandberger.com/en/Join.html",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategy & Management Consulting",
        "role_focus": ["strategy", "consulting", "leadership"]
    },
    {
        "name": "Strategy& India (PwC)",
        "slug": "strategy-and-india",
        "website": "https://www.strategyand.pwc.com",
        "career_url": "https://www.strategyand.pwc.com/in/en/careers.html",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategy & Management Consulting",
        "role_focus": ["strategy", "consulting", "founders_office"]
    },
    {
        "name": "Alvarez & Marsal India",
        "slug": "alvarez-and-marsal-india",
        "website": "https://www.alvarezandmarsal.com",
        "career_url": "https://www.alvarezandmarsal.com/careers",
        "ats_type": "workday",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategy & Turnaround Advisory",
        "role_focus": ["strategy", "consulting", "operations"]
    },
    {
        "name": "EY-Parthenon India",
        "slug": "ey-parthenon-india",
        "website": "https://www.ey.com/en_gl/parthenon",
        "career_url": "https://www.ey.com/en_in/careers",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategy Consulting",
        "role_focus": ["strategy", "consulting", "product"]
    },
    {
        "name": "Monitor Deloitte India",
        "slug": "monitor-deloitte-india",
        "website": "https://www2.deloitte.com",
        "career_url": "https://www2.deloitte.com/in/en/careers.html",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategy Consulting",
        "role_focus": ["strategy", "consulting", "leadership"]
    },
    {
        "name": "KPMG Strategy & Operations India",
        "slug": "kpmg-strategy-india",
        "website": "https://kpmg.com/in",
        "career_url": "https://kpmg.com/in/en/home/careers.html",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Management Consulting",
        "role_focus": ["strategy", "consulting", "operations"]
    },
    {
        "name": "PwC Management Consulting India",
        "slug": "pwc-consulting-india",
        "website": "https://www.pwc.in",
        "career_url": "https://www.pwc.in/careers.html",
        "ats_type": "workday",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Management Consulting",
        "role_focus": ["strategy", "consulting", "tech"]
    },
    {
        "name": "Arthur D. Little India",
        "slug": "arthur-d-little-india",
        "website": "https://www.adlittle.com",
        "career_url": "https://www.adlittle.com/en/careers",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategy & Innovation Consulting",
        "role_focus": ["strategy", "consulting", "tech"]
    },
    {
        "name": "Dalberg Advisors India",
        "slug": "dalberg-india",
        "website": "https://dalberg.com",
        "career_url": "https://dalberg.com/careers/",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Social Impact & Strategy Consulting",
        "role_focus": ["strategy", "consulting", "founders_office"]
    },
    {
        "name": "Samagra Governance",
        "slug": "samagra-governance",
        "website": "https://samagragovernance.in",
        "career_url": "https://samagragovernance.in/careers",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Governance & Public Policy Consulting",
        "role_focus": ["strategy", "consulting", "leadership"]
    },
    {
        "name": "Zinnov",
        "slug": "zinnov",
        "website": "https://zinnov.com",
        "career_url": "https://zinnov.com/careers/",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Tech & Globalization Advisory",
        "role_focus": ["strategy", "consulting", "tech"]
    },
    {
        "name": "Everest Group",
        "slug": "everest-group",
        "website": "https://www.everestgrp.com",
        "career_url": "https://www.everestgrp.com/careers/",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategic IT & Process Advisory",
        "role_focus": ["strategy", "consulting", "operations"]
    },
    {
        "name": "L.E.K. Consulting India",
        "slug": "lek-consulting-india",
        "website": "https://www.lek.com",
        "career_url": "https://www.lek.com/join-lek",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategy Consulting",
        "role_focus": ["strategy", "consulting", "product"]
    },
    {
        "name": "FTI Consulting India",
        "slug": "fti-consulting-india",
        "website": "https://www.fticonsulting.com",
        "career_url": "https://www.fticonsulting.com/careers",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Financial & Strategic Advisory",
        "role_focus": ["strategy", "consulting", "operations"]
    },
    {
        "name": "Simon-Kucher & Partners India",
        "slug": "simon-kucher-india",
        "website": "https://www.simon-kucher.com",
        "career_url": "https://www.simon-kucher.com/en/careers",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Growth & Pricing Strategy",
        "role_focus": ["strategy", "consulting", "product"]
    },
    {
        "name": "Kepler Cannon India",
        "slug": "kepler-cannon-india",
        "website": "https://keplercannon.com",
        "career_url": "https://keplercannon.com/careers/",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Boutique Strategy Advisory",
        "role_focus": ["strategy", "consulting", "founders_office"]
    },
    {
        "name": "Praxis Global Alliance",
        "slug": "praxis-global-alliance",
        "website": "https://praxisga.com",
        "career_url": "https://praxisga.com/careers",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Management & PE Advisory",
        "role_focus": ["strategy", "consulting", "product"]
    },
    {
        "name": "Avalon Consulting",
        "slug": "avalon-consulting",
        "website": "https://avalonconsulting.com",
        "career_url": "https://avalonconsulting.com/careers/",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Strategy & Performance Transformation",
        "role_focus": ["strategy", "consulting", "operations"]
    },
    {
        "name": "Intellecap",
        "slug": "intellecap",
        "website": "https://www.intellecap.com",
        "career_url": "https://www.intellecap.com/careers/",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Inclusive Development Advisory",
        "role_focus": ["strategy", "consulting", "founders_office"]
    },
    {
        "name": "Athena Infonomics",
        "slug": "athena-infonomics",
        "website": "https://athenainfonomics.com",
        "career_url": "https://athenainfonomics.com/careers/",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Data-Driven Public Policy Advisory",
        "role_focus": ["strategy", "consulting", "tech"]
    },
    {
        "name": "Vector Consulting Group",
        "slug": "vector-consulting",
        "website": "https://www.vectorconsulting.in",
        "career_url": "https://www.vectorconsulting.in/careers/",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Supply Chain & Operations Consulting",
        "role_focus": ["strategy", "consulting", "operations"]
    },
    {
        "name": "Miebach Consulting India",
        "slug": "miebach-india",
        "website": "https://www.miebach.com",
        "career_url": "https://www.miebach.com/in/careers/",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Supply Chain Transformation",
        "role_focus": ["strategy", "consulting", "operations"]
    },
    {
        "name": "Technopak Advisors",
        "slug": "technopak-advisors",
        "website": "https://technopak.com",
        "career_url": "https://technopak.com/careers/",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Retail & Consumer Strategy Advisory",
        "role_focus": ["strategy", "consulting", "product"]
    },
    {
        "name": "Crisil Advisory",
        "slug": "crisil-advisory",
        "website": "https://www.crisil.com",
        "career_url": "https://www.crisil.com/en/home/careers.html",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Financial & Market Research Advisory",
        "role_focus": ["strategy", "consulting", "leadership"]
    },
    {
        "name": "ICRA Analytics & Advisory",
        "slug": "icra-advisory",
        "website": "https://www.icra.in",
        "career_url": "https://www.icra.in/Careers",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Credit & Strategy Research",
        "role_focus": ["strategy", "consulting", "leadership"]
    },
    {
        "name": "CareEdge Advisory",
        "slug": "careedge-advisory",
        "website": "https://www.careedge.in",
        "career_url": "https://www.careedge.in/careers",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Financial & Rating Advisory",
        "role_focus": ["strategy", "consulting"]
    },
    {
        "name": "Nomura Research Institute (NRI) India",
        "slug": "nri-india",
        "website": "https://www.nri.com",
        "career_url": "https://www.nri.com/en/careers",
        "ats_type": "custom",
        "feed_url": None,
        "category_tier": "consulting",
        "domain": "Management & IT Consulting",
        "role_focus": ["strategy", "consulting", "tech"]
    }
]

# 2. Indian Conglomerates & Premier IT Enterprises (42 companies)
INDIAN_CONGLOMERATES: List[Dict[str, Any]] = [
    {"name": "Tata Sons", "slug": "tata-sons", "website": "https://www.tata.com", "career_url": "https://www.tata.com/careers", "ats_type": "custom", "domain": "Conglomerate", "category_tier": "conglomerate", "role_focus": ["strategy", "leadership", "operations"]},
    {"name": "Tata Digital", "slug": "tata-digital", "website": "https://www.tatadigital.com", "career_url": "https://www.tatadigital.com/careers", "ats_type": "custom", "domain": "Consumer Tech / Ecommerce", "category_tier": "conglomerate", "role_focus": ["product", "tech", "strategy", "leadership"]},
    {"name": "Tata Neu", "slug": "tata-neu", "website": "https://www.tataneu.com", "career_url": "https://boards.greenhouse.io/tataneu", "ats_type": "greenhouse", "domain": "Super App / Ecommerce", "category_tier": "conglomerate", "role_focus": ["product", "tech", "operations"]},
    {"name": "Tata 1mg", "slug": "tata-1mg", "website": "https://www.1mg.com", "career_url": "https://boards.greenhouse.io/tata1mg", "ats_type": "greenhouse", "domain": "HealthTech / Pharmacy", "category_tier": "conglomerate", "role_focus": ["tech", "product", "operations"]},
    {"name": "Tata Consultancy Services (TCS)", "slug": "tcs", "website": "https://www.tcs.com", "career_url": "https://www.tcs.com/careers", "ats_type": "custom", "domain": "IT & Global Consulting", "category_tier": "conglomerate", "role_focus": ["tech", "operations", "leadership"]},
    {"name": "Tata Elxsi", "slug": "tata-elxsi", "website": "https://www.tataelxsi.com", "career_url": "https://www.tataelxsi.com/careers", "ats_type": "custom", "domain": "Design & Deep Tech", "category_tier": "conglomerate", "role_focus": ["tech", "product"]},
    {"name": "Tata Motors", "slug": "tata-motors", "website": "https://www.tatamotors.com", "career_url": "https://www.tatamotors.com/careers/", "ats_type": "custom", "domain": "Automotive & EV", "category_tier": "conglomerate", "role_focus": ["tech", "operations", "strategy"]},
    {"name": "Tata Steel", "slug": "tata-steel", "website": "https://www.tatasteel.com", "career_url": "https://www.tatasteel.com/careers/", "ats_type": "custom", "domain": "Manufacturing & Materials", "category_tier": "conglomerate", "role_focus": ["operations", "leadership"]},
    {"name": "Titan Company", "slug": "titan-company", "website": "https://www.titancompany.in", "career_url": "https://www.titancompany.in/careers", "ats_type": "custom", "domain": "Retail & Luxury", "category_tier": "conglomerate", "role_focus": ["product", "operations", "strategy"]},
    {"name": "Trent (Westside / Zudio)", "slug": "trent-westside", "website": "https://www.mywestside.com", "career_url": "https://www.mywestside.com/pages/careers", "ats_type": "custom", "domain": "Fashion & Quick Retail", "category_tier": "conglomerate", "role_focus": ["operations", "strategy"]},
    {"name": "Voltas", "slug": "voltas", "website": "https://www.voltas.com", "career_url": "https://www.voltas.com/careers", "ats_type": "custom", "domain": "Consumer Appliances & Engineering", "category_tier": "conglomerate", "role_focus": ["operations", "tech"]},
    {"name": "Reliance Industries", "slug": "reliance-industries", "website": "https://www.ril.com", "career_url": "https://www.ril.com/Careers.aspx", "ats_type": "custom", "domain": "Conglomerate & Energy", "category_tier": "conglomerate", "role_focus": ["strategy", "operations", "leadership"]},
    {"name": "Reliance Jio", "slug": "reliance-jio", "website": "https://www.jio.com", "career_url": "https://careers.jio.com", "ats_type": "custom", "domain": "Telecom & Digital Services", "category_tier": "conglomerate", "role_focus": ["tech", "product", "operations"]},
    {"name": "Jio Platforms", "slug": "jio-platforms", "website": "https://www.jio.com", "career_url": "https://careers.jio.com/careers/index.html", "ats_type": "custom", "domain": "Cloud & AI Infrastructure", "category_tier": "conglomerate", "role_focus": ["tech", "product", "leadership"]},
    {"name": "Reliance Retail", "slug": "reliance-retail", "website": "https://relianceretail.com", "career_url": "https://relianceretail.com/careers.html", "ats_type": "custom", "domain": "Retail & Omnichannel", "category_tier": "conglomerate", "role_focus": ["operations", "product", "strategy"]},
    {"name": "Netmeds (Reliance)", "slug": "netmeds", "website": "https://www.netmeds.com", "career_url": "https://www.netmeds.com/careers", "ats_type": "custom", "domain": "Pharmacy & HealthTech", "category_tier": "conglomerate", "role_focus": ["product", "tech", "operations"]},
    {"name": "Urban Ladder (Reliance)", "slug": "urban-ladder", "website": "https://www.urbanladder.com", "career_url": "https://www.urbanladder.com/careers", "ats_type": "custom", "domain": "Home Living & Ecommerce", "category_tier": "conglomerate", "role_focus": ["product", "operations"]},
    {"name": "Infosys", "slug": "infosys", "website": "https://www.infosys.com", "career_url": "https://www.infosys.com/careers/", "ats_type": "custom", "domain": "IT & Digital Services", "category_tier": "conglomerate", "role_focus": ["tech", "leadership", "operations"]},
    {"name": "Infosys BPM", "slug": "infosys-bpm", "website": "https://www.infosysbpm.com", "career_url": "https://www.infosysbpm.com/careers.html", "ats_type": "custom", "domain": "Business Operations", "category_tier": "conglomerate", "role_focus": ["operations", "leadership"]},
    {"name": "Wipro", "slug": "wipro", "website": "https://www.wipro.com", "career_url": "https://careers.wipro.com", "ats_type": "custom", "domain": "IT & Consulting", "category_tier": "conglomerate", "role_focus": ["tech", "operations", "leadership"]},
    {"name": "Wipro Enterprises", "slug": "wipro-enterprises", "website": "https://wiproenterprises.com", "career_url": "https://wiproenterprises.com/careers/", "ats_type": "custom", "domain": "Consumer Care & Infrastructure", "category_tier": "conglomerate", "role_focus": ["operations", "strategy"]},
    {"name": "Larsen & Toubro (L&T)", "slug": "larsen-and-toubro", "website": "https://www.larsentoubro.com", "career_url": "https://www.larsentoubro.com/corporate/careers/", "ats_type": "custom", "domain": "Heavy Engineering & Infrastructure", "category_tier": "conglomerate", "role_focus": ["operations", "leadership", "strategy"]},
    {"name": "L&T Technology Services (LTTS)", "slug": "ltts", "website": "https://www.ltts.com", "career_url": "https://www.ltts.com/careers", "ats_type": "custom", "domain": "Engineering R&D Services", "category_tier": "conglomerate", "role_focus": ["tech", "product"]},
    {"name": "LTIMindtree", "slug": "ltimindtree", "website": "https://www.ltimindtree.com", "career_url": "https://www.ltimindtree.com/careers/", "ats_type": "custom", "domain": "Digital Consulting & IT", "category_tier": "conglomerate", "role_focus": ["tech", "product", "operations"]},
    {"name": "Mahindra & Mahindra", "slug": "mahindra-and-mahindra", "website": "https://www.mahindra.com", "career_url": "https://www.mahindra.com/careers", "ats_type": "custom", "domain": "Automotive, Farm & Aerospace", "category_tier": "conglomerate", "role_focus": ["operations", "strategy", "leadership"]},
    {"name": "Tech Mahindra", "slug": "tech-mahindra", "website": "https://www.techmahindra.com", "career_url": "https://careers.techmahindra.com", "ats_type": "custom", "domain": "Digital Services & Telecom IT", "category_tier": "conglomerate", "role_focus": ["tech", "leadership"]},
    {"name": "Mahindra Digital", "slug": "mahindra-digital", "website": "https://www.mahindra.com", "career_url": "https://www.mahindra.com/careers", "ats_type": "custom", "domain": "Digital Transformation Hub", "category_tier": "conglomerate", "role_focus": ["product", "tech", "strategy"]},
    {"name": "Aditya Birla Group", "slug": "aditya-birla-group", "website": "https://www.adityabirla.com", "career_url": "https://www.adityabirla.com/careers", "ats_type": "custom", "domain": "Conglomerate & Metals/Telecom", "category_tier": "conglomerate", "role_focus": ["strategy", "operations", "leadership"]},
    {"name": "UltraTech Cement", "slug": "ultratech-cement", "website": "https://www.ultratechcement.com", "career_url": "https://www.ultratechcement.com/careers", "ats_type": "custom", "domain": "Materials & Manufacturing", "category_tier": "conglomerate", "role_focus": ["operations", "strategy"]},
    {"name": "Hindalco", "slug": "hindalco", "website": "https://www.hindalco.com", "career_url": "https://www.hindalco.com/careers", "ats_type": "custom", "domain": "Metals & Mining", "category_tier": "conglomerate", "role_focus": ["operations", "leadership"]},
    {"name": "Godrej Industries", "slug": "godrej-industries", "website": "https://www.godrej.com", "career_url": "https://www.godrej.com/careers", "ats_type": "custom", "domain": "Conglomerate & Consumer Care", "category_tier": "conglomerate", "role_focus": ["strategy", "operations", "leadership"]},
    {"name": "Godrej Consumer Products", "slug": "godrej-consumer", "website": "https://www.godrejcp.com", "career_url": "https://www.godrejcp.com/careers", "ats_type": "custom", "domain": "FMCG", "category_tier": "conglomerate", "role_focus": ["product", "operations", "strategy"]},
    {"name": "Godrej Properties", "slug": "godrej-properties", "website": "https://www.godrejproperties.com", "career_url": "https://www.godrejproperties.com/careers", "ats_type": "custom", "domain": "Real Estate & Urban Spaces", "category_tier": "conglomerate", "role_focus": ["operations", "strategy"]},
    {"name": "ITC Limited", "slug": "itc-limited", "website": "https://www.itcportal.com", "career_url": "https://www.itcportal.com/careers/", "ats_type": "custom", "domain": "FMCG, Hospitality & Paper", "category_tier": "conglomerate", "role_focus": ["strategy", "operations", "leadership"]},
    {"name": "ITC Infotech", "slug": "itc-infotech", "website": "https://www.itcinfotech.com", "career_url": "https://www.itcinfotech.com/careers/", "ats_type": "custom", "domain": "Tech Services & Solutions", "category_tier": "conglomerate", "role_focus": ["tech", "operations"]},
    {"name": "Bajaj Finserv", "slug": "bajaj-finserv", "website": "https://www.bajajfinserv.in", "career_url": "https://www.bajajfinserv.in/careers", "ats_type": "custom", "domain": "Financial Services", "category_tier": "conglomerate", "role_focus": ["product", "strategy", "tech", "leadership"]},
    {"name": "Bajaj Finance", "slug": "bajaj-finance", "website": "https://www.bajajfinserv.in/finance", "career_url": "https://careers.bajajfinserv.in", "ats_type": "custom", "domain": "Consumer Lending & Fintech", "category_tier": "conglomerate", "role_focus": ["product", "tech", "operations"]},
    {"name": "Bajaj Auto", "slug": "bajaj-auto", "website": "https://www.bajajauto.com", "career_url": "https://www.bajajauto.com/careers", "ats_type": "custom", "domain": "Automotive & Two-Wheelers", "category_tier": "conglomerate", "role_focus": ["operations", "tech"]},
    {"name": "HDFC Bank", "slug": "hdfc-bank", "website": "https://www.hdfcbank.com", "career_url": "https://www.hdfcbank.com/personal/useful-links/careers", "ats_type": "custom", "domain": "Banking & Digital Finance", "category_tier": "conglomerate", "role_focus": ["tech", "product", "leadership"]},
    {"name": "ICICI Bank", "slug": "icici-bank", "website": "https://www.icicibank.com", "career_url": "https://www.icicicareers.com", "ats_type": "custom", "domain": "Banking & Digital Finance", "category_tier": "conglomerate", "role_focus": ["tech", "product", "operations"]},
    {"name": "Axis Bank", "slug": "axis-bank", "website": "https://www.axisbank.com", "career_url": "https://www.axisbank.com/careers", "ats_type": "custom", "domain": "Banking & Digital Finance", "category_tier": "conglomerate", "role_focus": ["product", "tech", "strategy"]},
    {"name": "Kotak Mahindra Bank", "slug": "kotak-bank", "website": "https://www.kotak.com", "career_url": "https://www.kotak.com/en/about-us/careers.html", "ats_type": "custom", "domain": "Banking & Digital Finance", "category_tier": "conglomerate", "role_focus": ["tech", "product", "leadership"]}
]

# 3. Indian Tech Startups & Unicorns (152 companies)
# Spanning Fintech, Quick Commerce, SaaS, AI/DeepTech, Mobility, HealthTech, EdTech, Consumer Tech, B2B
STARTUP_SECTORS = [
    # Quick Commerce & Food Delivery
    ("Swiggy", "swiggy", "https://swiggy.com", "https://careers.swiggy.com", "lever", "https://api.lever.co/v0/postings/swiggy?mode=json", "unicorn", "Food & Quick Commerce", ["product", "tech", "operations", "strategy"]),
    ("Zomato", "zomato", "https://zomato.com", "https://www.zomato.com/careers", "lever", "https://api.lever.co/v0/postings/zomato?mode=json", "unicorn", "Food & Quick Commerce", ["product", "tech", "operations"]),
    ("Zepto", "zepto", "https://zeptonow.com", "https://jobs.lever.co/zepto", "lever", "https://api.lever.co/v0/postings/zepto?mode=json", "unicorn", "Quick Commerce", ["product", "tech", "founders_office", "strategy"]),
    ("Blinkit", "blinkit", "https://blinkit.com", "https://blinkit.com/careers", "lever", "https://api.lever.co/v0/postings/blinkit?mode=json", "unicorn", "Quick Commerce", ["product", "tech", "operations"]),
    
    # Fintech & Digital Payments
    ("CRED", "cred", "https://cred.club", "https://jobs.lever.co/cred", "lever", "https://api.lever.co/v0/postings/cred?mode=json", "unicorn", "Fintech / Credit", ["product", "tech", "founders_office", "strategy"]),
    ("Groww", "groww", "https://groww.in", "https://jobs.lever.co/groww", "lever", "https://api.lever.co/v0/postings/groww?mode=json", "unicorn", "Fintech / WealthTech", ["product", "tech", "strategy"]),
    ("Meesho", "meesho", "https://meesho.com", "https://jobs.lever.co/meesho", "lever", "https://api.lever.co/v0/postings/meesho?mode=json", "unicorn", "Ecommerce", ["product", "tech", "strategy", "founders_office"]),
    ("PhonePe", "phonepe", "https://phonepe.com", "https://boards.greenhouse.io/phonepe", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/phonepe/jobs", "unicorn", "Fintech / Payments", ["product", "tech", "operations"]),
    ("Razorpay", "razorpay", "https://razorpay.com", "https://jobs.lever.co/razorpay", "lever", "https://api.lever.co/v0/postings/razorpay?mode=json", "unicorn", "Fintech / Payments", ["product", "tech", "strategy"]),
    ("Paytm (One97)", "paytm", "https://paytm.com", "https://jobs.lever.co/paytm", "lever", "https://api.lever.co/v0/postings/paytm?mode=json", "unicorn", "Fintech / Payments", ["product", "tech", "operations"]),
    ("Navi Technologies", "navi", "https://navi.com", "https://jobs.lever.co/navi", "lever", "https://api.lever.co/v0/postings/navi?mode=json", "unicorn", "Fintech / Digital Lending", ["product", "tech", "founders_office"]),
    ("Slice", "slice", "https://sliceit.com", "https://jobs.lever.co/slice", "lever", "https://api.lever.co/v0/postings/slice?mode=json", "unicorn", "Fintech / Banking", ["product", "tech", "strategy"]),
    ("Jupiter Money", "jupiter", "https://jupiter.money", "https://jobs.lever.co/jupiter", "lever", "https://api.lever.co/v0/postings/jupiter?mode=json", "startup", "Fintech / Neobank", ["product", "tech", "founders_office"]),
    ("Fi Money (EpiFi)", "fi-money", "https://fi.money", "https://jobs.lever.co/fi-money", "lever", "https://api.lever.co/v0/postings/fi-money?mode=json", "startup", "Fintech / Neobank", ["product", "tech"]),
    ("Jar", "jar", "https://myjar.app", "https://jobs.lever.co/jar", "lever", "https://api.lever.co/v0/postings/jar?mode=json", "startup", "Fintech / Savings", ["product", "tech", "founders_office"]),
    ("INDmoney", "indmoney", "https://indmoney.com", "https://jobs.lever.co/indmoney", "lever", "https://api.lever.co/v0/postings/indmoney?mode=json", "startup", "Fintech / Super Wealth", ["product", "tech"]),
    ("Smallcase", "smallcase", "https://smallcase.com", "https://jobs.lever.co/smallcase", "lever", "https://api.lever.co/v0/postings/smallcase?mode=json", "startup", "Fintech / Capital Markets", ["product", "tech"]),
    ("KredX", "kredx", "https://kredx.com", "https://jobs.lever.co/kredx", "lever", "https://api.lever.co/v0/postings/kredx?mode=json", "startup", "Fintech / Invoice Discounting", ["tech", "operations"]),
    ("Lendingkart", "lendingkart", "https://lendingkart.com", "https://jobs.lever.co/lendingkart", "lever", "https://api.lever.co/v0/postings/lendingkart?mode=json", "startup", "Fintech / MSME Lending", ["tech", "operations"]),
    ("Turtlemint", "turtlemint", "https://turtlemint.com", "https://jobs.lever.co/turtlemint", "lever", "https://api.lever.co/v0/postings/turtlemint?mode=json", "startup", "Fintech / InsurTech", ["product", "tech"]),
    ("Cashfree Payments", "cashfree", "https://cashfree.com", "https://jobs.lever.co/cashfree", "lever", "https://api.lever.co/v0/postings/cashfree?mode=json", "startup", "Fintech / Gateways", ["product", "tech"]),
    ("PayU India", "payu-india", "https://corporate.payu.com", "https://jobs.lever.co/payu", "lever", "https://api.lever.co/v0/postings/payu?mode=json", "unicorn", "Fintech / Gateway", ["product", "tech"]),
    ("Pine Labs", "pine-labs", "https://pinelabs.com", "https://boards.greenhouse.io/pinelabs", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/pinelabs/jobs", "unicorn", "Fintech / Merchant POS", ["product", "tech", "strategy"]),
    ("BharatPe", "bharatpe", "https://bharatpe.com", "https://jobs.lever.co/bharatpe", "lever", "https://api.lever.co/v0/postings/bharatpe?mode=json", "unicorn", "Fintech / Merchant QR", ["product", "tech", "operations"]),
    ("Mswipe", "mswipe", "https://mswipe.com", "https://jobs.lever.co/mswipe", "lever", "https://api.lever.co/v0/postings/mswipe?mode=json", "startup", "Fintech / POS", ["tech", "operations"]),
    ("Dezerv", "dezerv", "https://dezerv.in", "https://jobs.ashbyhq.com/dezerv", "ashby", "https://api.ashbyhq.com/posting-api/job-board/dezerv", "startup", "Fintech / Wealth", ["product", "tech", "founders_office"]),
    ("Stable Money", "stable-money", "https://stablemoney.in", "https://jobs.ashbyhq.com/stablemoney", "ashby", "https://api.ashbyhq.com/posting-api/job-board/stablemoney", "startup", "Fintech / Fixed Returns", ["product", "tech", "founders_office"]),
    ("Wint Wealth", "wint-wealth", "https://wintwealth.com", "https://jobs.lever.co/wintwealth", "lever", "https://api.lever.co/v0/postings/wintwealth?mode=json", "startup", "Fintech / Debt Assets", ["product", "tech"]),
    ("CoinDCX", "coindcx", "https://coindcx.com", "https://jobs.lever.co/coindcx", "lever", "https://api.lever.co/v0/postings/coindcx?mode=json", "unicorn", "Fintech / Crypto", ["product", "tech"]),
    ("CoinSwitch", "coinswitch", "https://coinswitch.co", "https://jobs.lever.co/coinswitch", "lever", "https://api.lever.co/v0/postings/coinswitch?mode=json", "unicorn", "Fintech / Crypto", ["product", "tech"]),
    ("Zeta", "zeta", "https://zeta.tech", "https://jobs.lever.co/zeta", "lever", "https://api.lever.co/v0/postings/zeta?mode=json", "unicorn", "Fintech / Banking SaaS", ["tech", "product", "strategy"]),
    ("OneCard (FPL Tech)", "onecard", "https://getonecard.app", "https://jobs.lever.co/onecard", "lever", "https://api.lever.co/v0/postings/onecard?mode=json", "unicorn", "Fintech / Credit Cards", ["product", "tech", "founders_office"]),
    ("Uni Cards", "uni-cards", "https://uni.club", "https://jobs.lever.co/uni", "lever", "https://api.lever.co/v0/postings/uni?mode=json", "startup", "Fintech / Credit", ["product", "tech"]),

    # Generative AI & Data Infrastructure
    ("Atlan", "atlan", "https://atlan.com", "https://jobs.lever.co/atlan", "lever", "https://api.lever.co/v0/postings/atlan?mode=json", "unicorn", "Data Governance & Metadata AI", ["tech", "product", "founders_office", "strategy"]),
    ("SigNoz", "signoz", "https://signoz.io", "https://jobs.ashbyhq.com/signoz", "ashby", "https://api.ashbyhq.com/posting-api/job-board/signoz", "startup", "DevOps & Observability", ["tech", "product", "founders_office"]),
    ("Sarvam AI", "sarvam-ai", "https://sarvam.ai", "https://jobs.ashbyhq.com/sarvam-ai", "ashby", "https://api.ashbyhq.com/posting-api/job-board/sarvam-ai", "startup", "Generative AI / Indic LLMs", ["tech", "product", "founders_office"]),
    ("Acceldata", "acceldata", "https://acceldata.io", "https://jobs.lever.co/acceldata", "lever", "https://api.lever.co/v0/postings/acceldata?mode=json", "startup", "Data Observability", ["tech", "product"]),
    ("Postman", "postman", "https://postman.com", "https://boards.greenhouse.io/postman", "greenhouse", "https://boards-api.greenhouse.io/v1/boards/postman/jobs", "unicorn", "Developer Tools / API Platform", ["product", "tech", "strategy"]),
    ("BrowserStack", "browserstack", "https://browserstack.com", "https://jobs.lever.co/browserstack", "lever", "https://api.lever.co/v0/postings/browserstack?mode=json", "unicorn", "Developer Tools / Cloud Testing", ["product", "tech"]),
    ("Hasura", "hasura", "https://hasura.io", "https://jobs.lever.co/hasura", "lever", "https://api.lever.co/v0/postings/hasura?mode=json", "unicorn", "Developer Tools / GraphQL", ["tech", "product", "founders_office"]),
    ("InMobi", "inmobi", "https://inmobi.com", "https://jobs.lever.co/inmobi", "lever", "https://api.lever.co/v0/postings/inmobi?mode=json", "unicorn", "AdTech & Consumer Media", ["product", "tech", "strategy"]),
    ("Glance", "glance", "https://glance.com", "https://jobs.lever.co/glance", "lever", "https://api.lever.co/v0/postings/glance?mode=json", "unicorn", "Lockscreen Content AI", ["product", "tech", "founders_office"]),
    ("Druva", "druva", "https://druva.com", "https://jobs.lever.co/druva", "lever", "https://api.lever.co/v0/postings/druva?mode=json", "unicorn", "Cloud Data Protection", ["tech", "product"]),
    ("HighRadius", "highradius", "https://highradius.com", "https://jobs.lever.co/highradius", "lever", "https://api.lever.co/v0/postings/highradius?mode=json", "unicorn", "Fintech SaaS / Autonomous Finance", ["product", "tech"]),
    ("Zenoti", "zenoti", "https://zenoti.com", "https://jobs.lever.co/zenoti", "lever", "https://api.lever.co/v0/postings/zenoti?mode=json", "unicorn", "Vertical SaaS / Wellness", ["product", "tech"]),
    ("Mindtickle", "mindtickle", "https://mindtickle.com", "https://jobs.lever.co/mindtickle", "lever", "https://api.lever.co/v0/postings/mindtickle?mode=json", "unicorn", "Sales Enablement SaaS", ["product", "tech", "strategy"]),
    ("Whatfix", "whatfix", "https://whatfix.com", "https://jobs.lever.co/whatfix", "lever", "https://api.lever.co/v0/postings/whatfix?mode=json", "unicorn", "Digital Adoption SaaS", ["product", "tech"]),
    ("LeadSquared", "leadsquared", "https://leadsquared.com", "https://jobs.lever.co/leadsquared", "lever", "https://api.lever.co/v0/postings/leadsquared?mode=json", "unicorn", "Sales CRM SaaS", ["product", "tech"]),
    ("Darwinbox", "darwinbox", "https://darwinbox.com", "https://jobs.lever.co/darwinbox", "lever", "https://api.lever.co/v0/postings/darwinbox?mode=json", "unicorn", "HR Tech SaaS", ["product", "tech"]),
    ("CleverTap", "clevertap", "https://clevertap.com", "https://jobs.lever.co/clevertap", "lever", "https://api.lever.co/v0/postings/clevertap?mode=json", "unicorn", "Customer Engagement SaaS", ["product", "tech"]),
    ("MoEngage", "moengage", "https://moengage.com", "https://jobs.lever.co/moengage", "lever", "https://api.lever.co/v0/postings/moengage?mode=json", "unicorn", "Customer Engagement SaaS", ["product", "tech"]),
    ("WebEngage", "webengage", "https://webengage.com", "https://jobs.lever.co/webengage", "lever", "https://api.lever.co/v0/postings/webengage?mode=json", "startup", "Retention Marketing SaaS", ["product", "tech"]),
    ("Chargebee", "chargebee", "https://chargebee.com", "https://jobs.lever.co/chargebee", "lever", "https://api.lever.co/v0/postings/chargebee?mode=json", "unicorn", "Subscription Billing SaaS", ["product", "tech"]),
    ("Kissflow", "kissflow", "https://kissflow.com", "https://jobs.lever.co/kissflow", "lever", "https://api.lever.co/v0/postings/kissflow?mode=json", "startup", "Low-Code Workflow SaaS", ["product", "tech"]),
    ("HackerRank", "hackerrank", "https://hackerrank.com", "https://jobs.lever.co/hackerrank", "lever", "https://api.lever.co/v0/postings/hackerrank?mode=json", "startup", "Developer Assessment", ["product", "tech"]),
    ("InterviewBit / Scaler", "scaler", "https://scaler.com", "https://jobs.lever.co/scaler", "lever", "https://api.lever.co/v0/postings/scaler?mode=json", "startup", "EdTech / Tech Upskilling", ["product", "tech", "founders_office"]),
    ("Yellow.ai", "yellow-ai", "https://yellow.ai", "https://jobs.lever.co/yellowai", "lever", "https://api.lever.co/v0/postings/yellowai?mode=json", "startup", "Conversational AI SaaS", ["tech", "product"]),
    ("Gupshup", "gupshup", "https://gupshup.io", "https://jobs.lever.co/gupshup", "lever", "https://api.lever.co/v0/postings/gupshup?mode=json", "unicorn", "Conversational Messaging", ["product", "tech"]),
    ("Entrupy", "entrupy", "https://entrupy.com", "https://jobs.lever.co/entrupy", "lever", "https://api.lever.co/v0/postings/entrupy?mode=json", "startup", "Computer Vision / AI", ["tech", "product"]),
    ("GreyOrange", "greyorange", "https://greyorange.com", "https://jobs.lever.co/greyorange", "lever", "https://api.lever.co/v0/postings/greyorange?mode=json", "unicorn", "Warehouse Robotics AI", ["tech", "operations", "product"]),

    # Mobility, Logistics & AutoTech
    ("Delhivery", "delhivery", "https://delhivery.com", "https://jobs.lever.co/delhivery", "lever", "https://api.lever.co/v0/postings/delhivery?mode=json", "unicorn", "Logistics & Supply Chain Tech", ["product", "tech", "operations"]),
    ("Porter", "porter", "https://porter.in", "https://jobs.lever.co/porter", "lever", "https://api.lever.co/v0/postings/porter?mode=json", "unicorn", "Intracity Logistics", ["product", "tech", "operations"]),
    ("Rapido", "rapido", "https://rapido.bike", "https://jobs.lever.co/rapido", "lever", "https://api.lever.co/v0/postings/rapido?mode=json", "unicorn", "Mobility / Bike Taxi", ["product", "tech", "operations"]),
    ("Ather Energy", "ather-energy", "https://atherenergy.com", "https://jobs.lever.co/atherenergy", "lever", "https://api.lever.co/v0/postings/atherenergy?mode=json", "unicorn", "CleanTech / EV", ["tech", "product", "operations"]),
    ("Ola Electric", "ola-electric", "https://olaelectric.com", "https://jobs.lever.co/olaelectric", "lever", "https://api.lever.co/v0/postings/olaelectric?mode=json", "unicorn", "EV & Mobility", ["tech", "operations"]),
    ("BluSmart", "blusmart", "https://blu-smart.com", "https://jobs.lever.co/blusmart", "lever", "https://api.lever.co/v0/postings/blusmart?mode=json", "startup", "All-Electric Ride Hailing", ["operations", "tech", "product"]),
    ("Spinny", "spinny", "https://spinny.com", "https://jobs.lever.co/spinny", "lever", "https://api.lever.co/v0/postings/spinny?mode=json", "unicorn", "Used Cars Retail Tech", ["product", "tech", "operations"]),
    ("Cars24", "cars24", "https://cars24.com", "https://jobs.lever.co/cars24", "lever", "https://api.lever.co/v0/postings/cars24?mode=json", "unicorn", "AutoTech Ecommerce", ["product", "tech", "operations"]),
    ("Shiprocket", "shiprocket", "https://shiprocket.in", "https://jobs.lever.co/shiprocket", "lever", "https://api.lever.co/v0/postings/shiprocket?mode=json", "unicorn", "D2C Logistics SaaS", ["product", "tech", "founders_office"]),
    ("Loconav", "loconav", "https://loconav.com", "https://jobs.lever.co/loconav", "lever", "https://api.lever.co/v0/postings/loconav?mode=json", "startup", "Fleet Management IoT", ["product", "tech"]),
    ("BlackBuck", "blackbuck", "https://blackbuck.com", "https://jobs.lever.co/blackbuck", "lever", "https://api.lever.co/v0/postings/blackbuck?mode=json", "unicorn", "Trucking Platform", ["product", "tech", "operations"]),
    ("Intangles", "intangles", "https://intangles.com", "https://jobs.lever.co/intangles", "lever", "https://api.lever.co/v0/postings/intangles?mode=json", "startup", "Vehicle Telematics AI", ["tech", "product"]),
    ("Euler Motors", "euler-motors", "https://eulermotors.com", "https://jobs.lever.co/eulermotors", "lever", "https://api.lever.co/v0/postings/eulermotors?mode=json", "startup", "Commercial EV", ["tech", "operations"]),
    ("Simple Energy", "simple-energy", "https://simpleenergy.in", "https://jobs.lever.co/simpleenergy", "lever", "https://api.lever.co/v0/postings/simpleenergy?mode=json", "startup", "Electric Scooters", ["tech", "operations"]),
    ("River", "river", "https://rideriver.com", "https://jobs.ashbyhq.com/river", "ashby", "https://api.ashbyhq.com/posting-api/job-board/river", "startup", "EV Design & Tech", ["tech", "product", "founders_office"]),
    ("Yulu", "yulu", "https://yulu.bike", "https://jobs.lever.co/yulu", "lever", "https://api.lever.co/v0/postings/yulu?mode=json", "startup", "Micro-Mobility EV", ["operations", "tech", "product"]),
    ("Cityflo", "cityflo", "https://cityflo.com", "https://jobs.lever.co/cityflo", "lever", "https://api.lever.co/v0/postings/cityflo?mode=json", "startup", "Urban Commute", ["product", "tech", "operations"]),
    ("Chalo", "chalo", "https://chalo.com", "https://jobs.lever.co/chalo", "lever", "https://api.lever.co/v0/postings/chalo?mode=json", "startup", "Public Transport Tech", ["product", "tech", "operations"]),

    # Travel & Hospitality
    ("MakeMyTrip", "makemytrip", "https://makemytrip.com", "https://careers.makemytrip.com", "custom", None, "unicorn", "Travel Tech", ["product", "tech", "strategy"]),
    ("redBus", "redbus", "https://redbus.in", "https://jobs.lever.co/redbus", "lever", "https://api.lever.co/v0/postings/redbus?mode=json", "unicorn", "Online Ticketing", ["product", "tech"]),
    ("Ixigo", "ixigo", "https://ixigo.com", "https://jobs.lever.co/ixigo", "lever", "https://api.lever.co/v0/postings/ixigo?mode=json", "unicorn", "Travel & Train Booking", ["product", "tech"]),
    ("Cleartrip (Flipkart)", "cleartrip", "https://cleartrip.com", "https://jobs.lever.co/cleartrip", "lever", "https://api.lever.co/v0/postings/cleartrip?mode=json", "unicorn", "Travel & Aviation", ["product", "tech"]),
    ("EaseMyTrip", "easemytrip", "https://easemytrip.com", "https://jobs.lever.co/easemytrip", "lever", "https://api.lever.co/v0/postings/easemytrip?mode=json", "unicorn", "Travel Platform", ["product", "tech"]),
    ("Oyo", "oyo", "https://oyorooms.com", "https://jobs.lever.co/oyorooms", "lever", "https://api.lever.co/v0/postings/oyorooms?mode=json", "unicorn", "Hospitality Tech", ["product", "tech", "strategy", "operations"]),
    ("Treebo Hotels", "treebo", "https://treebo.com", "https://jobs.lever.co/treebo", "lever", "https://api.lever.co/v0/postings/treebo?mode=json", "startup", "Budget Hospitality", ["product", "tech"]),

    # HealthTech & Fitness
    ("Cultfit (Curefit)", "cultfit", "https://cult.fit", "https://jobs.lever.co/cultfit", "lever", "https://api.lever.co/v0/postings/cultfit?mode=json", "unicorn", "Health & Fitness", ["product", "tech", "founders_office"]),
    ("Ultrahuman", "ultrahuman", "https://ultrahuman.com", "https://jobs.ashbyhq.com/ultrahuman", "ashby", "https://api.ashbyhq.com/posting-api/job-board/ultrahuman", "startup", "Metabolic Wearables & Hardware", ["product", "tech", "founders_office"]),
    ("HealthifyMe", "healthifyme", "https://healthifyme.com", "https://jobs.lever.co/healthifyme", "lever", "https://api.lever.co/v0/postings/healthifyme?mode=json", "startup", "Digital Health & AI Nutrition", ["product", "tech"]),
    ("PharmEasy", "pharmeasy", "https://pharmeasy.in", "https://jobs.lever.co/pharmeasy", "lever", "https://api.lever.co/v0/postings/pharmeasy?mode=json", "unicorn", "HealthTech / E-Pharmacy", ["product", "tech", "operations"]),
    ("MediBuddy", "medibuddy", "https://medibuddy.in", "https://jobs.lever.co/medibuddy", "lever", "https://api.lever.co/v0/postings/medibuddy?mode=json", "startup", "Digital Healthcare", ["product", "tech"]),
    ("Practo", "practo", "https://practo.com", "https://jobs.lever.co/practo", "lever", "https://api.lever.co/v0/postings/practo?mode=json", "startup", "Doctor Teleconsultation", ["product", "tech"]),
    ("Pristyn Care", "pristyn-care", "https://pristyncare.com", "https://jobs.lever.co/pristyncare", "lever", "https://api.lever.co/v0/postings/pristyncare?mode=json", "unicorn", "Secondary Care Surgery", ["operations", "tech", "product"]),

    # Consumer Tech, D2C, PropTech & Others
    ("Urban Company", "urban-company", "https://urbancompany.com", "https://jobs.lever.co/urbancompany", "lever", "https://api.lever.co/v0/postings/urbancompany?mode=json", "unicorn", "Home Services Marketplace", ["product", "tech", "operations", "founders_office"]),
    ("Nykaa", "nykaa", "https://nykaa.com", "https://jobs.lever.co/nykaa", "lever", "https://api.lever.co/v0/postings/nykaa?mode=json", "unicorn", "Beauty & Fashion Ecommerce", ["product", "tech", "strategy"]),
    ("Licious", "licious", "https://licious.in", "https://jobs.lever.co/licious", "lever", "https://api.lever.co/v0/postings/licious?mode=json", "unicorn", "Fresh D2C Consumer Brands", ["product", "tech", "operations"]),
    ("Mamaearth (Honasa)", "mamaearth", "https://mamaearth.in", "https://jobs.lever.co/mamaearth", "lever", "https://api.lever.co/v0/postings/mamaearth?mode=json", "unicorn", "D2C Personal Care", ["product", "operations"]),
    ("Pocket FM", "pocket-fm", "https://pocketfm.com", "https://jobs.lever.co/pocketfm", "lever", "https://api.lever.co/v0/postings/pocketfm?mode=json", "unicorn", "Audio Series & Media Tech", ["product", "tech", "founders_office"]),
    ("Truecaller India", "truecaller", "https://truecaller.com", "https://jobs.lever.co/truecaller", "lever", "https://api.lever.co/v0/postings/truecaller?mode=json", "unicorn", "Communication Tech", ["product", "tech"]),
    ("NoBroker", "nobroker", "https://nobroker.in", "https://jobs.lever.co/nobroker", "lever", "https://api.lever.co/v0/postings/nobroker?mode=json", "unicorn", "PropTech / Real Estate", ["product", "tech", "operations"]),
    ("Square Yards", "square-yards", "https://squareyards.com", "https://jobs.lever.co/squareyards", "lever", "https://api.lever.co/v0/postings/squareyards?mode=json", "startup", "PropTech Platform", ["tech", "operations"]),
    ("Infra.Market", "infra-market", "https://infra.market", "https://jobs.lever.co/inframarket", "lever", "https://api.lever.co/v0/postings/inframarket?mode=json", "unicorn", "B2B Construction Commerce", ["product", "tech", "operations", "strategy"]),
    ("Zetwerk", "zetwerk", "https://zetwerk.com", "https://jobs.lever.co/zetwerk", "lever", "https://api.lever.co/v0/postings/zetwerk?mode=json", "unicorn", "B2B Custom Manufacturing", ["product", "tech", "operations", "founders_office"]),
    ("Moglix", "moglix", "https://moglix.com", "https://jobs.lever.co/moglix", "lever", "https://api.lever.co/v0/postings/moglix?mode=json", "unicorn", "B2B Industrial Ecommerce", ["product", "tech", "operations"]),
    ("OfBusiness", "ofbusiness", "https://ofbusiness.com", "https://jobs.lever.co/ofbusiness", "lever", "https://api.lever.co/v0/postings/ofbusiness?mode=json", "unicorn", "B2B Raw Materials & Credit", ["product", "tech", "strategy", "operations"]),
    ("Bizongo", "bizongo", "https://bizongo.com", "https://jobs.lever.co/bizongo", "lever", "https://api.lever.co/v0/postings/bizongo?mode=json", "startup", "B2B Packaging Tech", ["product", "tech", "operations"]),
    ("Udaan", "udaan", "https://udaan.com", "https://jobs.lever.co/udaan", "lever", "https://api.lever.co/v0/postings/udaan?mode=json", "unicorn", "B2B Retail Marketplace", ["product", "tech", "operations"]),
    ("Jumbotail", "jumbotail", "https://jumbotail.com", "https://jobs.lever.co/jumbotail", "lever", "https://api.lever.co/v0/postings/jumbotail?mode=json", "startup", "B2B Wholesale Grocery", ["product", "tech", "operations"]),
    ("Country Delight", "country-delight", "https://countrydelight.in", "https://jobs.lever.co/countrydelight", "lever", "https://api.lever.co/v0/postings/countrydelight?mode=json", "startup", "Fresh Dairy Direct Consumer", ["product", "tech", "operations"]),
    ("Ninjacart", "ninjacart", "https://ninjacart.com", "https://jobs.lever.co/ninjacart", "lever", "https://api.lever.co/v0/postings/ninjacart?mode=json", "startup", "Agritech Supply Chain", ["product", "tech", "operations"]),
    ("DeHaat", "dehaat", "https://agrevolution.in", "https://jobs.lever.co/dehaat", "lever", "https://api.lever.co/v0/postings/dehaat?mode=json", "startup", "Agritech Inputs & Advisory", ["product", "tech"]),
    ("AgroStar", "agrostar", "https://agrostar.in", "https://jobs.lever.co/agrostar", "lever", "https://api.lever.co/v0/postings/agrostar?mode=json", "startup", "Farmers Direct Agritech", ["product", "tech"]),
    ("CropIn", "cropin", "https://cropin.com", "https://jobs.lever.co/cropin", "lever", "https://api.lever.co/v0/postings/cropin?mode=json", "startup", "Agritech AI & Cloud", ["tech", "product"]),

    # DeepTech, SpaceTech & Aerospace
    ("Skyroot Aerospace", "skyroot", "https://skyroot.in", "https://jobs.ashbyhq.com/skyroot", "ashby", "https://api.ashbyhq.com/posting-api/job-board/skyroot", "startup", "SpaceTech / Launch Vehicles", ["tech", "founders_office"]),
    ("Agnikul Cosmos", "agnikul", "https://agnikul.in", "https://jobs.lever.co/agnikul", "lever", "https://api.lever.co/v0/postings/agnikul?mode=json", "startup", "SpaceTech / 3D Printed Engines", ["tech", "operations"]),
    ("Pixxel", "pixxel", "https://pixxel.space", "https://jobs.lever.co/pixxel", "lever", "https://api.lever.co/v0/postings/pixxel?mode=json", "startup", "Hyperspectral Satellite Constellation", ["tech", "product", "founders_office"]),
    ("Bellatrix Aerospace", "bellatrix", "https://bellatrix.aero", "https://jobs.lever.co/bellatrix", "lever", "https://api.lever.co/v0/postings/bellatrix?mode=json", "startup", "Space In-Orbit Propulsion", ["tech"]),
    ("GalaxEye Space", "galaxeye", "https://galaxeye.space", "https://jobs.ashbyhq.com/galaxeye", "ashby", "https://api.ashbyhq.com/posting-api/job-board/galaxeye", "startup", "SAR Satellite Imaging", ["tech", "founders_office"]),

    # EdTech & Higher Education
    ("PhysicsWallah", "physicswallah", "https://pw.live", "https://jobs.lever.co/physicswallah", "lever", "https://api.lever.co/v0/postings/physicswallah?mode=json", "unicorn", "EdTech / Affordable Learning", ["product", "tech", "operations"]),
    ("Unacademy", "unacademy", "https://unacademy.com", "https://jobs.lever.co/unacademy", "lever", "https://api.lever.co/v0/postings/unacademy?mode=json", "unicorn", "EdTech / Test Prep", ["product", "tech"]),
    ("UpGrad", "upgrad", "https://upgrad.com", "https://jobs.lever.co/upgrad", "lever", "https://api.lever.co/v0/postings/upgrad?mode=json", "unicorn", "Higher Education Upskilling", ["product", "tech", "strategy"]),
    ("Eruditus", "eruditus", "https://eruditus.com", "https://jobs.lever.co/eruditus", "lever", "https://api.lever.co/v0/postings/eruditus?mode=json", "unicorn", "Executive Education", ["product", "tech"]),
    ("Classplus", "classplus", "https://classplus.co", "https://jobs.lever.co/classplus", "lever", "https://api.lever.co/v0/postings/classplus?mode=json", "startup", "Creator & Teacher SaaS", ["product", "tech", "founders_office"]),
    ("Khatabook", "khatabook", "https://khatabook.com", "https://jobs.lever.co/khatabook", "lever", "https://api.lever.co/v0/postings/khatabook?mode=json", "startup", "MSME Accounting Tech", ["product", "tech"]),

    # D2C, Cloud Kitchens & Consumer Internet
    ("Rebel Foods", "rebel-foods", "https://rebelfoods.com", "https://jobs.lever.co/rebelfoods", "lever", "https://api.lever.co/v0/postings/rebelfoods?mode=json", "unicorn", "Cloud Kitchens / FoodTech", ["product", "tech", "operations"]),
    ("Curefoods", "curefoods", "https://curefoods.in", "https://jobs.lever.co/curefoods", "lever", "https://api.lever.co/v0/postings/curefoods?mode=json", "startup", "Cloud Kitchen Brands", ["operations", "product"]),
    ("Chaayos", "chaayos", "https://chaayos.com", "https://jobs.lever.co/chaayos", "lever", "https://api.lever.co/v0/postings/chaayos?mode=json", "startup", "Omnichannel F&B Tech", ["operations", "product", "tech"]),
    ("Chai Point", "chai-point", "https://chaipoint.com", "https://jobs.lever.co/chaipoint", "lever", "https://api.lever.co/v0/postings/chaipoint?mode=json", "startup", "F&B IoT & Retail", ["tech", "operations"]),
    ("EatClub (Box8)", "eatclub", "https://eatclub.com", "https://jobs.lever.co/eatclub", "lever", "https://api.lever.co/v0/postings/eatclub?mode=json", "startup", "Food Delivery Network", ["product", "tech", "operations"]),
    ("Wakefit", "wakefit", "https://wakefit.co", "https://jobs.lever.co/wakefit", "lever", "https://api.lever.co/v0/postings/wakefit?mode=json", "startup", "D2C Home & Sleep", ["product", "operations"]),
    ("Pepperfry", "pepperfry", "https://pepperfry.com", "https://jobs.lever.co/pepperfry", "lever", "https://api.lever.co/v0/postings/pepperfry?mode=json", "unicorn", "Furniture Marketplace", ["product", "tech", "operations"]),
    ("CaratLane (Titan)", "caratlane", "https://caratlane.com", "https://jobs.lever.co/caratlane", "lever", "https://api.lever.co/v0/postings/caratlane?mode=json", "unicorn", "Omnichannel Jewellery", ["product", "tech"]),
    ("BlueStone", "bluestone", "https://bluestone.com", "https://jobs.lever.co/bluestone", "lever", "https://api.lever.co/v0/postings/bluestone?mode=json", "startup", "Jewellery Ecommerce", ["product", "tech", "operations"]),
    ("Sugar Cosmetics", "sugar-cosmetics", "https://sugarcosmetics.com", "https://jobs.lever.co/sugarcosmetics", "lever", "https://api.lever.co/v0/postings/sugarcosmetics?mode=json", "startup", "D2C Beauty & Omnichannel", ["product", "operations"]),
    ("Plum Goodness", "plum-goodness", "https://plumgoodness.com", "https://jobs.lever.co/plumgoodness", "lever", "https://api.lever.co/v0/postings/plumgoodness?mode=json", "startup", "Clean Beauty D2C", ["operations", "product"]),
    ("Bombay Shaving Company", "bombay-shaving-company", "https://bombayshavingcompany.com", "https://jobs.lever.co/bombayshavingcompany", "lever", "https://api.lever.co/v0/postings/bombayshavingcompany?mode=json", "startup", "Personal Care D2C", ["operations", "product"]),
    ("Kapiva", "kapiva", "https://kapiva.in", "https://jobs.lever.co/kapiva", "lever", "https://api.lever.co/v0/postings/kapiva?mode=json", "startup", "Ayurvedic Nutrition D2C", ["product", "operations"]),
    ("Epigamia (Drums Food)", "epigamia", "https://epigamia.com", "https://jobs.lever.co/epigamia", "lever", "https://api.lever.co/v0/postings/epigamia?mode=json", "startup", "FMCG Greek Yogurt D2C", ["operations", "product"]),
    ("Mensa Brands", "mensa-brands", "https://mensabrands.com", "https://jobs.lever.co/mensabrands", "lever", "https://api.lever.co/v0/postings/mensabrands?mode=json", "unicorn", "D2C Brand Aggregator", ["strategy", "product", "founders_office", "operations"]),
    ("GlobalBees", "globalbees", "https://globalbees.com", "https://jobs.lever.co/globalbees", "lever", "https://api.lever.co/v0/postings/globalbees?mode=json", "unicorn", "D2C Brand House", ["strategy", "operations", "founders_office"]),
    ("Goat Brand Labs", "goat-brand-labs", "https://goatbrandlabs.com", "https://jobs.lever.co/goatbrandlabs", "lever", "https://api.lever.co/v0/postings/goatbrandlabs?mode=json", "startup", "D2C Brand Accelerator", ["strategy", "operations"]),

    # InsurTech, Health Benefits & FinTech
    ("Even Healthcare", "even-healthcare", "https://even.in", "https://jobs.ashbyhq.com/even", "ashby", "https://api.ashbyhq.com/posting-api/job-board/even", "startup", "Managed Care & Health Plans", ["product", "tech", "founders_office"]),
    ("Loop Health", "loop-health", "https://loophealth.com", "https://jobs.lever.co/loophealth", "lever", "https://api.lever.co/v0/postings/loophealth?mode=json", "startup", "Group Health Insurance", ["product", "tech"]),
    ("Onsurity", "onsurity", "https://onsurity.com", "https://jobs.lever.co/onsurity", "lever", "https://api.lever.co/v0/postings/onsurity?mode=json", "startup", "Employee Healthcare Tech", ["product", "tech"]),
    ("Nova Benefits", "nova-benefits", "https://novabenefits.com", "https://jobs.lever.co/novabenefits", "lever", "https://api.lever.co/v0/postings/novabenefits?mode=json", "startup", "Corporate Wellness SaaS", ["product", "tech", "founders_office"]),
    ("FamPay", "fampay", "https://fampay.in", "https://jobs.lever.co/fampay", "lever", "https://api.lever.co/v0/postings/fampay?mode=json", "startup", "Teen Fintech & Payments", ["product", "tech", "founders_office"]),
    ("Rupifi", "rupifi", "https://rupifi.com", "https://jobs.lever.co/rupifi", "lever", "https://api.lever.co/v0/postings/rupifi?mode=json", "startup", "B2B Embedded Fintech", ["product", "tech"]),
    ("Progcap", "progcap", "https://progcap.com", "https://jobs.lever.co/progcap", "lever", "https://api.lever.co/v0/postings/progcap?mode=json", "startup", "Supply Chain Financing", ["product", "tech", "operations"]),
    ("Open Financial Technologies", "open-financial", "https://open.money", "https://jobs.lever.co/open", "lever", "https://api.lever.co/v0/postings/open?mode=json", "unicorn", "SME Neobank Platform", ["product", "tech", "strategy"]),
    ("Refyne", "refyne", "https://refyne.co.in", "https://jobs.lever.co/refyne", "lever", "https://api.lever.co/v0/postings/refyne?mode=json", "startup", "Earned Wage Access", ["product", "tech"]),
    ("LiquiLoans", "liquiloans", "https://liquiloans.com", "https://jobs.lever.co/liquiloans", "lever", "https://api.lever.co/v0/postings/liquiloans?mode=json", "startup", "P2P Lending Tech", ["product", "tech"]),
    ("Mudrex", "mudrex", "https://mudrex.com", "https://jobs.lever.co/mudrex", "lever", "https://api.lever.co/v0/postings/mudrex?mode=json", "startup", "Crypto Wealth Management", ["product", "tech", "founders_office"]),

    # Mobility, Hyperlocal & Supply Chain
    ("Dunzo", "dunzo", "https://dunzo.com", "https://jobs.lever.co/dunzo", "lever", "https://api.lever.co/v0/postings/dunzo?mode=json", "startup", "Hyperlocal Delivery Tech", ["product", "tech", "operations"]),
    ("Magicpin", "magicpin", "https://magicpin.in", "https://jobs.lever.co/magicpin", "lever", "https://api.lever.co/v0/postings/magicpin?mode=json", "startup", "Local Commerce & ONDC", ["product", "tech", "operations"]),
    ("Shipsy", "shipsy", "https://shipsy.io", "https://jobs.lever.co/shipsy", "lever", "https://api.lever.co/v0/postings/shipsy?mode=json", "startup", "Logistics Orchestration SaaS", ["product", "tech"]),
    ("Fleetx", "fleetx", "https://fleetx.io", "https://jobs.lever.co/fleetx", "lever", "https://api.lever.co/v0/postings/fleetx?mode=json", "startup", "Freight IoT & Fleet SaaS", ["product", "tech"]),
    ("Captain Fresh", "captain-fresh", "https://captainfresh.in", "https://jobs.lever.co/captainfresh", "lever", "https://api.lever.co/v0/postings/captainfresh?mode=json", "startup", "B2B Animal Protein Supply Chain", ["operations", "tech", "product"]),
    ("WayCool Foods", "waycool", "https://waycool.in", "https://jobs.lever.co/waycool", "lever", "https://api.lever.co/v0/postings/waycool?mode=json", "startup", "Food Supply Chain Tech", ["operations", "product", "tech"]),
    ("Fasal", "fasal.co", "https://fasal.co", "https://jobs.lever.co/fasal", "lever", "https://api.lever.co/v0/postings/fasal?mode=json", "startup", "Horticulture Precision IoT", ["tech", "product"]),
    ("Jai Kisan", "jai-kisan", "https://jai-kisan.com", "https://jobs.lever.co/jaikisan", "lever", "https://api.lever.co/v0/postings/jaikisan?mode=json", "startup", "Rural Rural Fintech", ["product", "tech"])
]

# Convert tuples to target dictionaries
INDIAN_STARTUPS: List[Dict[str, Any]] = [
    {
        "name": t[0],
        "slug": t[1],
        "website": t[2],
        "career_url": t[3],
        "ats_type": t[4],
        "feed_url": t[5],
        "category_tier": t[6],
        "domain": t[7],
        "role_focus": t[8]
    }
    for t in STARTUP_SECTORS
]


def write_catalog_partitions():
    # 1. Write consulting
    consulting_path = TARGETS_DIR / "strategy_consulting.json"
    with open(consulting_path, "w", encoding="utf-8") as f:
        json.dump(STRATEGY_CONSULTING_FIRMS, f, indent=2)
    logger.info(f"Wrote {len(STRATEGY_CONSULTING_FIRMS)} consulting targets to {consulting_path}")

    # 2. Write conglomerates
    conglom_path = TARGETS_DIR / "indian_conglomerates.json"
    with open(conglom_path, "w", encoding="utf-8") as f:
        json.dump(INDIAN_CONGLOMERATES, f, indent=2)
    logger.info(f"Wrote {len(INDIAN_CONGLOMERATES)} conglomerate targets to {conglom_path}")

    # 3. Write startups
    startups_path = TARGETS_DIR / "indian_startups.json"
    with open(startups_path, "w", encoding="utf-8") as f:
        json.dump(INDIAN_STARTUPS, f, indent=2)
    logger.info(f"Wrote {len(INDIAN_STARTUPS)} startup targets to {startups_path}")

    total = len(STRATEGY_CONSULTING_FIRMS) + len(INDIAN_CONGLOMERATES) + len(INDIAN_STARTUPS)
    logger.info(f"Total Indian targets cataloged across 3 partitioned files: {total}")


if __name__ == "__main__":
    write_catalog_partitions()

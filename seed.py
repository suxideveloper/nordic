"""Seed script — creates sample Partners, Events, Vacancies, Internships, Grants."""
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordic_uni.settings')
django.setup()

from django.utils import timezone
from datetime import date, timedelta
from core.models import Partner, SiteSettings
from events.models import Event, EventCategory
from opportunities.models import (
    Vacancy, VacancyCategory,
    Internship,
    Grant, GrantCategory
)

# ─── Site Settings ────────────────────────────────────────
s = SiteSettings.get_settings()
s.telegram = 'https://t.me/nordicuniversity'
s.instagram = 'https://instagram.com/nordicuniversity.uz'
s.linkedin = 'https://linkedin.com/school/nordic-university-tashkent'
s.save()
print("SiteSettings updated")

# ─── Partners ─────────────────────────────────────────────
partners_data = [
    ("EPAM Systems", "https://epam.com", "Global software engineering and IT consulting company."),
    ("IT Park Uzbekistan", "https://it-park.uz", "Government-backed technology park in Tashkent."),
    ("Uzum", "https://uzum.uz", "Uzbekistan's leading e-commerce platform."),
    ("Kapital Bank", "https://kapitalbank.uz", "One of Uzbekistan's top commercial banks."),
    ("British Council", "https://britishcouncil.uz", "UK's international organisation for cultural relations and educational opportunities."),
    ("DAAD Germany", "https://daad.de", "German Academic Exchange Service — scholarships and research grants."),
    ("Technovation", "https://technovation.org", "Global tech education nonprofit for young people."),
    ("Huawei Uzbekistan", "https://huawei.com", "Global technology and telecommunications company."),
]
partners = []
for name, url, desc in partners_data:
    p, _ = Partner.objects.get_or_create(name=name, defaults={"website": url, "description": desc})
    partners.append(p)
print(f"Partners: {len(partners)} created")

# ─── Event Categories ─────────────────────────────────────
cat_conf, _ = EventCategory.objects.get_or_create(name="Conference", slug="conference", defaults={"icon": "bi-mic-fill", "color": "#6C63FF"})
cat_hack, _ = EventCategory.objects.get_or_create(name="Hackathon", slug="hackathon", defaults={"icon": "bi-lightning-fill", "color": "#FF6B35"})
cat_ws, _   = EventCategory.objects.get_or_create(name="Workshop", slug="workshop", defaults={"icon": "bi-tools", "color": "#00D4AA"})
cat_job, _  = EventCategory.objects.get_or_create(name="Career Fair", slug="career-fair", defaults={"icon": "bi-briefcase-fill", "color": "#FFD166"})

events_data = [
    ("TechTalks Tashkent 2025", "techtalks-tashkent-2025", cat_conf, partners[1], "Annual technology conference bringing together innovators, startups, and industry leaders.", "online", True, 14),
    ("AI Hackathon by EPAM", "ai-hackathon-epam-2025", cat_hack, partners[0], "48-hour AI/ML hackathon open to all Nordic students. Build the future with code.", "offline", True, 21),
    ("Web Dev Workshop Series", "web-dev-workshop-2025", cat_ws, partners[0], "A series of hands-on workshops covering React, Django, and modern web development.", "hybrid", True, 7),
    ("Nordic Career Fair 2025", "nordic-career-fair-2025", cat_job, None, "Connect directly with leading employers. Bring your CV and ambition!", "offline", True, 30),
    ("Cloud Summit Uzbekistan", "cloud-summit-uz-2025", cat_conf, partners[7], "Deep dive into cloud computing, DevOps, and enterprise architecture.", "online", True, 45),
]
for title, slug, cat, org, desc, fmt, free, days in events_data:
    Event.objects.get_or_create(slug=slug, defaults={
        "title": title, "category": cat, "organizer": org,
        "short_description": desc, "description": f"<p>{desc}</p><p>Join us for a day of learning, networking and collaboration. Open to all Nordic University students and alumni.</p>",
        "start_date": timezone.now() + timedelta(days=days),
        "format": fmt, "is_free": free, "is_published": True, "is_featured": True,
        "location": "IT Park, Tashkent" if fmt != "online" else "Online (Zoom)",
    })
print("Events created")

# ─── Vacancy Categories ───────────────────────────────────
vcat_it, _  = VacancyCategory.objects.get_or_create(name="IT & Software", slug="it-software")
vcat_fin, _ = VacancyCategory.objects.get_or_create(name="Finance", slug="finance")
vcat_mkt, _ = VacancyCategory.objects.get_or_create(name="Marketing", slug="marketing")

vacancies_data = [
    ("Junior Python Developer", "junior-python-developer", partners[0], vcat_it, "full_time", "Tashkent", 800, 1200, True),
    ("Frontend Developer (React)", "frontend-developer-react", partners[2], vcat_it, "full_time", "Tashkent / Remote", 1000, 1800, True),
    ("Data Analyst Intern→Junior", "data-analyst-junior", partners[3], vcat_fin, "full_time", "Tashkent", 600, 900, True),
    ("Digital Marketing Specialist", "digital-marketing-specialist", partners[2], vcat_mkt, "full_time", "Tashkent", 700, 1100, False),
    ("Cloud Solutions Architect", "cloud-solutions-architect", partners[7], vcat_it, "remote", "Remote", 2000, 3500, False),
]
for title, slug, partner, cat, emp, loc, smin, smax, for_stud in vacancies_data:
    Vacancy.objects.get_or_create(slug=slug, defaults={
        "title": title, "partner": partner, "category": cat,
        "employment_type": emp, "location": loc, "salary_min": smin, "salary_max": smax,
        "is_for_students": for_stud, "is_active": True,
        "short_description": f"We are looking for a talented {title} to join our team.",
        "description": f"<p>We are looking for a talented <strong>{title}</strong> to join our growing team at {partner.name}.</p><p>This is a great opportunity to work on real-world projects and grow your career.</p>",
        "requirements": "<ul><li>Strong problem-solving skills</li><li>Relevant technical background</li><li>Good communication skills</li><li>Ability to work in a team</li></ul>",
        "deadline": date.today() + timedelta(days=30),
        "apply_url": partner.website,
    })
print("Vacancies created")

# ─── Internships ──────────────────────────────────────────
internships_data = [
    ("Software Engineering Intern", "software-engineering-intern-epam", partners[0], "3_months", "Tashkent", True, 400),
    ("UX/UI Design Intern", "ux-ui-design-intern-uzum", partners[2], "2_months", "Tashkent", True, 300),
    ("Data Science Research Intern", "data-science-intern-it-park", partners[1], "6_months", "Tashkent", False, 0),
    ("Cybersecurity Intern", "cybersecurity-intern-huawei", partners[7], "3_months", "Tashkent / Beijing", True, 500),
]
for title, slug, partner, dur, loc, paid, stipend in internships_data:
    Internship.objects.get_or_create(slug=slug, defaults={
        "title": title, "partner": partner, "duration": dur, "location": loc,
        "is_paid": paid, "stipend": stipend if paid else None,
        "is_active": True, "field_of_study": "Computer Science, IT, Engineering",
        "short_description": f"Internship opportunity at {partner.name} — gain real experience in {title.replace(' Intern','').lower()}.",
        "description": f"<p><strong>{partner.name}</strong> is offering an exciting internship in <em>{title.replace(' Intern','')}</em>.</p><p>This program is designed for students who want to gain hands-on experience, work alongside senior professionals, and contribute to real projects.</p>",
        "deadline": date.today() + timedelta(days=20),
        "apply_url": partner.website,
    })
print("Internships created")

# ─── Grant Categories ─────────────────────────────────────
gcat_sch, _ = GrantCategory.objects.get_or_create(name="Scholarship", slug="scholarship-grants")
gcat_res, _ = GrantCategory.objects.get_or_create(name="Research", slug="research-grants")

grants_data = [
    ("Erasmus+ Scholarship 2025", "erasmus-plus-2025", partners[4], "scholarship", "Europe", True, None, gcat_sch),
    ("DAAD Scholarships for Uzbek Students", "daad-uzbekistan-2025", partners[5], "scholarship", "Germany", True, 10000, gcat_sch),
    ("British Council GREAT Scholarship", "british-council-great-2025", partners[4], "scholarship", "United Kingdom", True, 15000, gcat_sch),
    ("Huawei Tech4Good Research Grant", "huawei-tech4good-2025", partners[7], "research", "Global", False, 5000, gcat_res),
]
for title, slug, partner, gtype, country, fully_funded, amount, cat in grants_data:
    Grant.objects.get_or_create(slug=slug, defaults={
        "title": title, "partner": partner, "grant_type": gtype, "country": country,
        "is_fully_funded": fully_funded, "amount": amount, "category": cat,
        "is_active": True, "is_featured": True,
        "short_description": f"Apply for {title} — a prestigious funding opportunity for Nordic University students.",
        "description": f"<p><strong>{title}</strong> is a prestigious funding opportunity offered by {partner.name}.</p><p>This grant supports Nordic University students who demonstrate academic excellence and a passion for making a global impact.</p>",
        "eligibility": "<ul><li>Enrolled at Nordic University Tashkent</li><li>GPA 3.0 or above</li><li>Proficiency in English</li><li>Motivation letter required</li></ul>",
        "deadline": date.today() + timedelta(days=45),
        "apply_url": partner.website,
    })
print("Grants created")
print("\n✅ Seed data complete!")

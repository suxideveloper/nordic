import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from articles.models import Category, Article


class Command(BaseCommand):
    help = 'Seeds fake articles and categories for student career guidance'

    def handle(self, *args, **options):
        self.stdout.write("Seeding categories...")

        # 1. Categories
        categories_data = [
            {
                "name": "Resume & CV",
                "icon": "bi bi-file-earmark-person",
                "color": "#00D4AA",
                "description": "Guides and templates on how to write professional resumes and cover letters."
            },
            {
                "name": "Interview Prep",
                "icon": "bi bi-chat-dots",
                "color": "#6C63FF",
                "description": "Tips, mock questions, and advice to help you ace your job interviews."
            },
            {
                "name": "Networking & LinkedIn",
                "icon": "bi bi-linkedin",
                "color": "#3b82f6",
                "description": "How to build a professional network and optimize your LinkedIn presence."
            },
            {
                "name": "Career Planning",
                "icon": "bi bi-compass",
                "color": "#FF6B35",
                "description": "Strategies for choosing the right career path, setting goals, and growing professionally."
            }
        ]

        categories = {}
        for cat_info in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_info["name"],
                defaults={
                    "icon": cat_info["icon"],
                    "color": cat_info["color"],
                    "description": cat_info["description"]
                }
            )
            categories[cat_info["name"]] = cat
            if created:
                self.stdout.write(f"Created category: {cat.name}")

        # Get or create a superuser/author
        author = User.objects.filter(is_staff=True).first()
        if not author:
            author = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
            self.stdout.write("Created default admin user as author.")

        # 2. Articles Data
        articles_data = [
            {
                "title": "How to Build a Standout Resume with No Experience",
                "category_name": "Resume & CV",
                "difficulty": "beginner",
                "read_time": 5,
                "tags": "Resume, CV, Freshman, Internship",
                "is_featured": True,
                "excerpt": "Landing your first job or internship can feel like a chicken-and-egg problem: you need experience to get a job, but you need a job to get experience. Here is how to break the cycle.",
                "content": """
                <p>Landing your first job or internship can feel like a chicken-and-egg problem: you need experience to get a job, but you need a job to get experience. Here is how to break the cycle by building a powerful resume that highlights your potential rather than your history.</p>
                
                <h3>1. Focus on Your Education and Projects</h3>
                <p>If you don't have professional work experience, your academic achievements and projects should take center stage. Mention relevant coursework, high GPAs (if above 3.5), and any significant university projects or group presentations.</p>
                <blockquote>"Projects demonstrate that you can apply theoretical knowledge to solve real-world problems."</blockquote>
                
                <h3>2. Highlight Extracurricular Activities</h3>
                <p>Are you part of a student club? Did you organize a university event? Active participation in student organizations shows leadership, teamwork, and organizational skills. Be sure to describe your specific contribution.</p>
                
                <h3>3. List Your Technical and Soft Skills</h3>
                <ul>
                    <li><strong>Technical Skills:</strong> Programming languages, design tools, MS Office, language proficiencies.</li>
                    <li><strong>Soft Skills:</strong> Communication, time management, adaptability, teamwork.</li>
                </ul>
                
                <h3>Conclusion</h3>
                <p>Keep your resume clean, error-free, and limited to one page. Focus on what you *can* do and how eager you are to learn.</p>
                """
            },
            {
                "title": "Top 5 Resume Mistakes Students Make (And How to Fix Them)",
                "category_name": "Resume & CV",
                "difficulty": "beginner",
                "read_time": 4,
                "tags": "Resume, Mistakes, Tips",
                "is_featured": False,
                "excerpt": "A single typo or poor formatting choice can cost you an interview. Avoid these five common student resume mistakes to increase your response rate.",
                "content": """
                <p>Your resume is your first impression. Recruiters spend an average of only 6 to 8 seconds scanning a resume before deciding if it's worth a closer look. Avoid these common pitfalls to make sure yours passes the test:</p>
                
                <h3>1. Using an Unprofessional Email Address</h3>
                <p>Still using that email from middle school? It's time to upgrade. Stick to a simple format: <code>firstname.lastname@email.com</code>.</p>
                
                <h3>2. Grammatical Errors and Typos</h3>
                <p>Typos suggest a lack of attention to detail. Always proofread your resume and ask a friend or mentor to read it over before submitting.</p>
                
                <h3>3. Listing Duties Instead of Accomplishments</h3>
                <p>Don't just list what you were supposed to do; tell recruiters what you actually achieved. Use action verbs and numbers where possible (e.g., "Increased event attendance by 20%" instead of "Helped organize events").</p>
                
                <h3>4. Sending a Generic Resume for Every Job</h3>
                <p>Customize your resume for every application. Read the job description carefully and match your skills to the keywords used by the employer.</p>
                
                <h3>5. Bad Formatting and Length</h3>
                <p>Keep it to a single page. Use clean fonts like Arial or Calibri, and use bullet points instead of long paragraphs to keep it scannable.</p>
                """
            },
            {
                "title": "How to Answer 'Tell Me About Yourself' in an Interview",
                "category_name": "Interview Prep",
                "difficulty": "intermediate",
                "read_time": 6,
                "tags": "Interview, Preparation, Speaking",
                "is_featured": True,
                "excerpt": "This is almost always the first question in any interview. Learn how to craft a compelling response using the Present-Past-Future framework.",
                "content": """
                <p>Almost every job interview starts with this open-ended question. It sets the tone for the rest of the conversation. Instead of reciting your entire CV, use the proven <strong>Present-Past-Future</strong> formula to deliver a structured, impressive response.</p>
                
                <h3>1. The Present (15-20 seconds)</h3>
                <p>Start with where you are right now. For example: <em>"I am currently a third-year student at Nordic University majoring in Computer Science, with a keen focus on web development..."</em></p>
                
                <h3>2. The Past (20-30 seconds)</h3>
                <p>Mention a key achievement or project that shows your capability: <em>"In my last semester, I led a team of three to build a student portal application that was used by over 100 students to track assignments..."</em></p>
                
                <h3>3. The Future (15-20 seconds)</h3>
                <p>Explain why you are sitting in this interview right now: <em>"I'm really excited about this internship because I want to apply my programming skills in a fast-paced team and learn from senior developers, and I know your company is a leader in this space."</em></p>
                
                <blockquote>Tip: Keep your total answer between 90 seconds and 2 minutes. Practice it out loud!</blockquote>
                """
            },
            {
                "title": "Smart Questions You Should Ask at the End of Your Interview",
                "category_name": "Interview Prep",
                "difficulty": "intermediate",
                "read_time": 5,
                "tags": "Interview, Questions, Hiring",
                "is_featured": False,
                "excerpt": "When the interviewer asks, 'Do you have any questions for us?' saying 'no' is a missed opportunity. Here are the best questions to ask.",
                "content": """
                <p>When the interviewer asks, "Do you have any questions for us?" the worst answer you can give is "No, I think we covered everything." Asking questions shows your curiosity, preparation, and genuine interest in the role.</p>
                
                <h3>Here are some great questions to ask:</h3>
                <ul>
                    <li><strong>"What does success look like in this role in the first 90 days?"</strong> (Shows you are goal-oriented)</li>
                    <li><strong>"Can you describe a typical day or week for someone in this position?"</strong> (Shows you want to understand the practical day-to-day work)</li>
                    <li><strong>"What do you enjoy most about working at this company?"</strong> (Builds personal rapport with the interviewer)</li>
                    <li><strong>"What are the next steps in the interview process?"</strong> (Demonstrates your interest in moving forward)</li>
                </ul>
                <p>Avoid asking about salary or benefits in the first round unless the interviewer brings it up first.</p>
                """
            },
            {
                "title": "LinkedIn Optimization: A Step-by-Step Guide for Students",
                "category_name": "Networking & LinkedIn",
                "difficulty": "beginner",
                "read_time": 7,
                "tags": "LinkedIn, Profile, Networking, Branding",
                "is_featured": True,
                "excerpt": "Over 90% of recruiters use LinkedIn to find candidates. If you don't have an optimized profile, you are invisible. Here is how to fix it.",
                "content": """
                <p>LinkedIn is no longer just an online resume; it is your professional landing page. Follow these steps to transform your profile from a ghost town to a recruiter magnet:</p>
                
                <h3>1. Professional Photo and Banner</h3>
                <p>Use a clean headshot with good lighting and a friendly expression. Add a custom background banner that relates to your industry (e.g., code, city skylines, or clean abstract designs).</p>
                
                <h3>2. Write a Headline That Highlights Skills, Not Just Titles</h3>
                <p>Instead of "Student at Nordic University", try: <em>"Computer Science Student at Nordic University | Aspiring Frontend Developer | React, JS, Python"</em>.</p>
                
                <h3>3. Tell a Story in Your 'About' Section</h3>
                <p>Write in the first person. Explain your passion, what you are studying, your key projects, and what kind of opportunities you are looking for.</p>
                
                <h3>4. Build Your Network</h3>
                <p>Connect with classmates, professors, university alumni, and professionals working in the roles you want to target. Always send a personalized note when connecting with people you don't know well.</p>
                """
            },
            {
                "title": "The Art of Cold Emailing for Internships",
                "category_name": "Networking & LinkedIn",
                "difficulty": "advanced",
                "read_time": 8,
                "tags": "Cold Email, Internships, Outreach",
                "is_featured": False,
                "excerpt": "Learn how to reach out to managers and recruiters directly to secure internships that aren't even advertised on job boards.",
                "content": """
                <p>Many internship opportunities are never posted publicly. Cold outreach allows you to tap into this hidden job market. Here is how to write a cold email that actually gets opened and replied to.</p>
                
                <h3>1. Find the Right Person</h3>
                <p>Don't email the general info@ company address. Use LinkedIn to find the team lead or hiring manager for the department you want to join.</p>
                
                <h3>2. Craft a Compelling Subject Line</h3>
                <p>Keep it short and relevant. For example: <em>"Nordic University CS Student — Frontend Internship Query"</em>.</p>
                
                <h3>3. Structure the Email</h3>
                <ul>
                    <li><strong>Greeting:</strong> Keep it professional (e.g., "Dear Mr. Karimov,").</li>
                    <li><strong>The Hook:</strong> State who you are and why you are writing immediately.</li>
                    <li><strong>The Value Proposition:</strong> Briefly mention a relevant project or skill that shows you can contribute.</li>
                    <li><strong>Call to Action (CTA):</strong> Ask for a brief 10-minute call, not a job directly (e.g., "Would you be open to a quick 10-minute chat next week to discuss your path and any future internship possibilities?").</li>
                </ul>
                """
            }
        ]

        self.stdout.write("Seeding articles...")
        for art_info in articles_data:
            cat = categories.get(art_info["category_name"])
            
            # Avoid duplicate slug creation issues by checking title
            article, created = Article.objects.get_or_create(
                title=art_info["title"],
                defaults={
                    "category": cat,
                    "author": author,
                    "difficulty": art_info["difficulty"],
                    "read_time": art_info["read_time"],
                    "tags": art_info["tags"],
                    "is_featured": art_info["is_featured"],
                    "is_published": True,
                    "excerpt": art_info["excerpt"],
                    "content": art_info["content"],
                    "published_at": timezone.now()
                }
            )
            
            if created:
                self.stdout.write(f"Created article: {article.title}")
            else:
                self.stdout.write(f"Article already exists: {article.title}")

        self.stdout.write(self.style.SUCCESS("Database seeded successfully with fake blog/articles data!"))

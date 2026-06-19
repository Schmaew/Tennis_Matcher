import time
import random
import os
import re
import sys
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. CONFIGURATION
# ==============================================================================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE_NAME = "sent_comment_topics"
NAME_PROFILE = "UnknownUser"

SEARCH_QUERY = "tennis"
TARGET_KEYWORDS = ["thai tennis", "tennis", "tennis partners"] 

COOLDOWN_MIN = 3
COOLDOWN_MAX = 10
IMAGE_FOLDER = os.path.join(os.getcwd(), "public", "comment")

# -- BOT SETTINGS ---
KEYWORD = "tenis"
TARGET_KEYWORD = ["thai tennis", "tennis", "tennis partnersg"]
COOLDOWN_MIN = 3 
COOLDOWN_MAX = 10
IMAGE_FOLDER = os.path.join(os.getcwd(), "public", "comment")
SPINTAX_TEMPLATES = [
    # Appreciation of courage
    {
        "text": """[ขอนับถือ|ขอชื่นชม|ศรัทธาใน]ความกล้าหาญของ[อาจารย์|อ.เฉลิมชัย|ท่านอาจารย์] และ[น้อมนำ|ขอนำ]คำสอนต่างๆที่[อาจารย์|ท่าน]ถ่ายทอดตลอดหลายสิบปีไปใช้ต่อครับ [สุดยอดครับ|เป็นกำลังใจให้ครับ] https://www.askajarn.com/chalermchaikositpipat""",
        "has_image": False 
    },

    # Faith and practice
    {
        "text": """[อาจารย์เฉลิมชัย|อ.เฉลิมชัย] มีแต่[คำสอนดีๆ|ข้อคิดดีๆ] [แสดงความกล้าหาญ|กล้าหาญมาก] 
และ[เชื่อในความถูกต้อง|ยึดมั่นในความถูกต้อง]และออกมาพูด[ไม่ต้องเกรงใจใคร|อย่างตรงไปตรงมา] 
ขอ[คารวะ|นับถือ]และ[น้อมรับ|จะนำไป]แนวทางปฏิบัติ[ต่อไปในชีวิต|มาใช้]ของผมเช่นกันครับ https://www.askajarn.com/chalermchaikositpipat""",
        "has_image": True
    },

    # Short and concise words of encouragement
    {
        "text": """[เป็นกำลังใจ|ขอส่งกำลังใจ]ให้[อาจารย์|ท่าน]ครับ [สู้ๆ|ทำต่อไป]ครับ [สังคม|พวกเรา]ต้องการ[คนจริง|คนแบบท่าน]ที่[กล้าพูด|กล้าทำ]เพื่อ[ความถูกต้อง|สังคม]ครับ https://www.askajarn.com/chalermchaikositpipat""",
        "has_image": True
    },
    
    # A message of gratitude for the reminder
    {
        "text": """[ฟังแล้ว|อ่านแล้ว]ได้[สติ|แง่คิด]มากครับ [ขอบคุณ|ขอบพระคุณ][อาจารย์|ท่านอาจารย์]ที่[ออกมาพูด|คอยเตือนสติ]พวกเราเสมอ [นับถือ|ศรัทธา]ใน[จุดยืน|อุดมการณ์]ครับ https://www.askajarn.com/chalermchaikositpipat""",
        "has_image": False
    },
    
    # Art and Dharma
    {
        "text": """[กราบ|ขอคารวะ]หัวใจ[ศิลปิน|ผู้ให้]ของอาจารย์ครับ ทั้ง[งานศิลปะ|ผลงาน]และ[ธรรมะ|แนวคิด]ที่ท่านมอบให้ [มีค่า|ประเมินค่าไม่ได้]จริงๆ [ขอให้ท่าน|ขอให้อาจารย์]สุขภาพแข็งแรงครับ https://www.askajarn.com/chalermchaikositpipat""",
        "has_image": False
    },
    
    # The following teacher work for a long time
    {
        "text": """ผม[ติดตาม|เป็นแฟนคลับ]อาจารย์มา[นาน|หลายปี] [ชอบ|ประทับใจ]ที่อาจารย์เป็นคน[ชัดเจน|ตรงไปตรงมา] [ไม่อ้อมค้อม|จริงใจ] [ขอสนับสนุน|ขอเชียร์]ให้ทำสิ่งดีๆ ต่อไปครับ https://www.askajarn.com/chalermchaikositpipat""",
        "has_image": False
    },    
    
    # Agreeing with the correctness
    {
        "text": """[ความจริง|สัจธรรม]ก็คือ[ความจริง|สัจธรรม]ครับ [อาจารย์|ท่าน]พูดได้[โดนใจ|ตรงใจ]มาก [ขอคารวะ|นับถือ]จากใจจริง [สุดยอด|เยี่ยม]มากครับ https://www.askajarn.com/chalermchaikositpipat""",
        "has_image": True
    },    
    
    # The style of the younger generation
    {
        "text": """[ท่าน|อาจารย์เฉลิมชัย]คือ[ต้นแบบ|ไอดอล]ของ[คนรุ่นหลัง|คนทำงานศิลปะ]ครับ [ขอบคุณ|ขอบพระคุณ]ที่[สร้างสรรค์|ทำ]สิ่งดีๆ ให้แผ่นดิน [จะจดจำ|จะระลึก]คำสอนไว้เสมอครับ https://www.askajarn.com/chalermchaikositpipat""",
        "has_image": False
    },
    
    # The Blessing line
    {
        "text": """ขอสิ่งศักดิ์สิทธิ์[คุ้มครอง|ปกปักรักษา][อาจารย์|อ.เฉลิมชัย]ครับ ขอให้[มีความสุข|สุขภาพแข็งแรง] อยู่[สอน|เตือนสติ]ลูกหลานไป[นานๆ|ตลอดไป]นะครับ https://www.askajarn.com/chalermchaikositpipat""",
        "has_image": False
    },
    
    # The Nature and Truth
    {
        "text": """ธรรมชาติและความจริง[ย่อมเป็นเช่นนั้น|เป็นอย่างนี้]ครับ [อาจารย์|ท่านอาจารย์]พูดได้[ตรงใจ|โดนใจ]มากครับ [ขอคารวะ|นับถือ]ใน[ความกล้าหาญ|จุดยืน]ของท่านครับ https://www.askajarn.com/chalermchaikositpipat""",
        "has_image": True
    },
    
]

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Missing SUPABASE_URL or SUPABASE_KEY in .env file.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. UTILITY FUNCTIONS
# ==============================================================================
def spin_text(text):
    while True:
        match = re.search(r'\[([^\[\]]+)\]', text)
        if not match: break
        choices = match.group(1).split('|')
        replacement = random.choice(choices)
        text = text.replace(match.group(0), replacement, 1)
    return text

def get_random_image(folder_path):
    if not os.path.exists(folder_path): return None
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return os.path.join(folder_path, random.choice(files)) if files else None

def human_typing(element, text):
    for char in text:
        if char == '\n': element.send_keys(Keys.SHIFT, Keys.ENTER)
        else: element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

def extract_topic_id(url):
    try:
        match = re.search(r'/topic/(\d+)', url)
        if match: return match.group(1)
        return url
    except: return url

def get_all_senders():
    try:
        response = supabase.table(TABLE_NAME).select("author").neq("author", "null").execute()
        
        sender_set = set()
        for item in response.data:
            if item.get('author'):
                sender_set.add(item['author'].strip())
        
        return sender_set
    except Exception as e:
        print(f"   Warning: Could not fetch sender history: {e}")
        return set()

def get_user_identity(driver):
    global NAME_PROFILE
    print("   [Identity] Checking user...")

    try:
        nav_elem = driver.find_element(By.CSS_SELECTOR, "div.pt-top-menu-logged-name span.name_user")
        if nav_elem.text.strip():
            NAME_PROFILE = nav_elem.text.strip()
            print(f"   [Identity] Found (Navbar): {NAME_PROFILE}")
            return NAME_PROFILE
    except: pass

    try:
        target_url = "https://pantip.com/settings/profile"
        if driver.current_url != target_url:
            driver.get(target_url)
            time.sleep(2)

        # --- Use data-test-id from HTML  ---
        print("   [Identity] Reading from Settings Profile...")
        
        wait = WebDriverWait(driver, 10)
        
        # 1. find Element nickname section
        nickname_section = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-test-id='setting-profile-nickname']"))
        )
        
        # 2. find Element name from h6 tag inside that section
        name_element = nickname_section.find_element(By.TAG_NAME, "h6")
        
        raw_name = name_element.text.strip()
        
        if raw_name:
            NAME_PROFILE = raw_name
            print(f"   [Identity] Found (Settings): {NAME_PROFILE}")
            return NAME_PROFILE

    except Exception as e:
        print(f"   [Identity] Error finding name: {e}")
        # Backup method: try to get from profile image alt attribute
        try:
            print("   [Identity] Trying backup method (Image Alt)...")
            img_elem = driver.find_element(By.CSS_SELECTOR, "div[data-test-id='setting-profile-image'] img")
            alt_name = img_elem.get_attribute("alt")
            if alt_name:
                NAME_PROFILE = alt_name
                print(f"   [Identity] Found (Image Alt): {NAME_PROFILE}")
                return NAME_PROFILE
        except: pass

    if NAME_PROFILE == "UnknownUser":
         print("   [Warning] Could not identify user. Proceeding as UnknownUser.")
         
    return NAME_PROFILE

# 3. DATABASE FUNCTIONS
# ==============================================================================
def db_check_exists(topic_id):
    try:
        res = supabase.table(TABLE_NAME).select("comment_topic_id").eq("comment_topic_id", str(topic_id)).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"   [Database] Warning: exists-check failed for {topic_id}: {e}")
        return False

def db_insert_pending_topic(topic_id, url):
    try:
        data = {
            "comment_topic_id": str(topic_id),
            "topic_link": url,
            "created_at": datetime.now().isoformat(),
            "process_status": "u",
            "messages": None
        }
        supabase.table(TABLE_NAME).insert(data).execute()
        print(f"   [Database] Inserted pending: {topic_id}")
    except Exception as e:
        print(f"   [Database] Error Insert failed: {e}")

def db_fetch_pending_topics(limit=5):
    res = supabase.table(TABLE_NAME).select("*").is_("messages", "null").eq("process_status", "u").limit(limit).execute()
    return res.data

def db_update_success_topic(topic_id, comment_body):
    try:
        data = {
            "author": NAME_PROFILE,
            "messages": comment_body,
            "process_status": "p"
        }
        supabase.table(TABLE_NAME).update(data).eq("comment_topic_id", str(topic_id)).execute()
        print(f"   [Database] Updated success: {topic_id}")
    except Exception as e:
        print(f"   [Database] Error Update failed: {e}")

def db_mark_not_send(topic_id):
    try:
        supabase.table(TABLE_NAME).update({"process_status": "n"}).eq("comment_topic_id", str(topic_id)).execute()
    except: pass


# 4. FUNCTIONS FOR MODES
# ==============================================================================
def run_find_mode(driver, max_topics):
    print(f"\n Scanning for '{SEARCH_QUERY}' topics...")
    print(f"   Target: Find {max_topics} NEW matching topics")
    
    print("   Fetching known sender accounts...")
    known_senders = get_all_senders()
    print(f"   Ignored Senders List ({len(known_senders)} accounts)")

    driver.get(f"https://pantip.com/search?q={SEARCH_QUERY}")
    time.sleep(3)
    
    found_count = 0
    visited_links_session = set()
    scroll_retry = 0 
    max_scroll_retry = 3
    
    while found_count < max_topics:
        topic_elements = driver.find_elements(By.CSS_SELECTOR, "li.pt-list-item h2 a")
        
        target_link = None
        
        for elem in topic_elements:
            try:
                link = elem.get_attribute('href')
                if not link: continue
                
                if link in visited_links_session:
                    continue
                
                target_link = link
                break 
            except: continue
        
        if not target_link:
            print(f"   [Topic] No new topics visible. Scrolling down... (Retry {scroll_retry}/{max_scroll_retry})")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Check the link new topics after scroll
            new_elements = driver.find_elements(By.CSS_SELECTOR, "li.pt-list-item h2 a")
            current_links = [e.get_attribute('href') for e in new_elements]
            
            if all(l in visited_links_session for l in current_links):
                scroll_retry += 1
                if scroll_retry >= max_scroll_retry:
                    print("   [End] Reached end of search results (No new items found after retries).")
                    break
            else:
                scroll_retry = 0
            
            continue

        scroll_retry = 0
        visited_links_session.add(target_link)
        topic_id = extract_topic_id(target_link)

        if db_check_exists(topic_id):
            continue

        try:
            print(f"\n   Checking ({found_count}/{max_topics}): {target_link}")
            driver.get(target_link)
            time.sleep(2)

            try:
                comment_boxes = driver.find_elements(By.CSS_SELECTOR, "div.display-post-wrapper.section-comment")

                found_my_team = False

                print(f"   -> Found {len(comment_boxes)} comments/replies.")

                for box in comment_boxes:
                    try:
                        # 2. หาชื่อคนโพสต์ "เฉพาะในกล่องนั้นๆ" (box.find_element) ไม่ใช่ driver.find_element
                        user_element = box.find_element(By.CSS_SELECTOR, "a.display-post-name")
                        user_name = user_element.text.strip()
        
                        if user_name in known_senders:
                            print(f"     [SKIP] Found comment by our team ({user_name}) in this topic.")
                            found_my_team = True
                            break
                            
                    except Exception as e:
                        continue

                if found_my_team:
                    driver.back()
                    time.sleep(1)
                    continue
            except Exception as e:
                print(f"     [Warning] Cannot check participants: {e}")
                
            title_txt = ""
            try: title_txt = driver.find_element(By.CSS_SELECTOR, ".display-post-title").text.strip()
            except: pass
            
            content_txt = ""
            try: 
                story_elems = driver.find_elements(By.CSS_SELECTOR, ".display-post-story")
                for s in story_elems: content_txt += s.text + " "
            except: pass
            try: 
                msg_elems = driver.find_elements(By.CSS_SELECTOR, ".display-post-message")
                for m in msg_elems: content_txt += m.text + " "
            except: pass

            comments_txt = ""
            try:
                # Pull Comment by Keyword
                comm_elems = driver.find_elements(By.CSS_SELECTOR, ".display-post-comment")
                for c in comm_elems:
                    comments_txt += c.text + " "
            except: pass
            
            full_text = (title_txt + " " + content_txt + " " + comments_txt).lower()

            # -- Check Keywords --
            is_match = False
            for kw in TARGET_KEYWORDS:
                if kw.lower() in full_text:
                    is_match = True
                    print(f"     [Match] Found Keyword: '{kw}'")
                    break
            
            if is_match:
                db_insert_pending_topic(topic_id, target_link)
                found_count += 1
                print(f"     [+] Saved to Unprocessed List (Total: {found_count})")
            else:
                print("     [-] Not related (Skipped)")

            driver.back()
            time.sleep(1)

        except Exception as e:
            print(f"Error processing topic: {e}")
            try: driver.back()
            except: pass

    print("\n" + "="*100)
    print(f"FINAL RESULT: Found & Saved {found_count} Topics")
    print("="*100)

def run_send_mode(driver, max_limit):
    print(f"\n MODE: SEND (COMMENTING on unprocessed topics)")
    
    get_user_identity(driver)
    if NAME_PROFILE == "UnknownUser":
        print("   [Warning]: Could not identify user. Proceeding as UnknownUser.")

    pending_list = db_fetch_pending_topics(limit=max_limit)
    if not pending_list:
        print("   [Database] No pending topics found.")
        return

    print(f"   [Cache] Loaded {len(pending_list)} pending topics.")

    for item in pending_list:
        topic_id = item['comment_topic_id']
        link = item['topic_link']

        print(f"\n------------------------------------------------")
        print(f"Processing ID: {topic_id}")
        
        try:
            driver.get(link)
            time.sleep(2)
            
            try:
                title_elem = driver.find_element(By.CSS_SELECTOR, ".display-post-title")
                print(f"Title: {title_elem.text}")
            except:
                print("Title: (Cannot read title)")

            user_input = input(">>> Process comment this topic? (y/n/s): ").strip().lower()

            if user_input == 's':
                print("Skipping...")
                continue
            
            elif user_input == 'n':
                print("Skipping...")
                db_mark_not_send(topic_id) # Update status nit send
                continue

            elif user_input == 'y':
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                editor_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.editor-input[contenteditable='true']"))
                )
                driver.execute_script("arguments[0].click();", editor_box)
                
                template = random.choice(SPINTAX_TEMPLATES)
                final_msg = spin_text(template["text"])
                
                print(f"   Writing: {final_msg[:40]}...")
                human_typing(editor_box, final_msg)
                
                if template["has_image"]:
                    img_path = get_random_image(IMAGE_FOLDER)
                    if img_path:
                        try:
                            file_input = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                            if file_input: file_input[0].send_keys(img_path)
                            else:
                                driver.find_element(By.CSS_SELECTOR, "button[aria-label='ใส่รูปประกอบ']").click()
                                time.sleep(1)
                                driver.find_element(By.CSS_SELECTOR, "input[type='file']").send_keys(img_path)
                            print(f"   Uploaded: {os.path.basename(img_path)}")
                            time.sleep(3)
                        except: print("   Image upload failed")

                # Submit Comment
                submit_btn = driver.find_element(By.ID, "btn_comment")
                if "disabled" not in (submit_btn.get_attribute("class") or ""):
                    driver.execute_script("arguments[0].click();", submit_btn)
                    print("   Clicked Submit!")
                    
                    time.sleep(3)

                    # Update DB
                    db_update_success_topic(topic_id, final_msg)
                else:
                    print("   Submit button disabled!")

                # Cooldown
                wait_t = random.randint(COOLDOWN_MIN * 60, COOLDOWN_MAX * 60)
                print(f"   Cooldown {wait_t}s...")
                time.sleep(wait_t)

        except Exception as e:
            print(f"Error processing topic {topic_id}: {e}")

# 5. MAIN EXECUTION
# ==============================================================================
def main():
    # Argument Parsing
    # Usage: python script.py [mode] [count]
    # Modes: find, send
    
    mode = "find"
    max_topics = 5

    if len(sys.argv) >= 2:
        mode = sys.argv[1].lower()
    if len(sys.argv) >= 3:
        try: max_topics = int(sys.argv[2])
        except: pass

    print(f"--- STARTING PANTIP BOT ---")
    print(f"Mode: {mode.upper()} COMMENT" if mode == "send" else f"Mode: {mode.upper()} COMMENT (Scanning {max_topics} topics)")
    
    # 1. Setup Driver
    options = Options()
    profile_path = os.path.join(os.getcwd(), "pantip_bot_profile")
    options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Clear stale Chrome singleton locks from a previously-killed run
    for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        lock_path = os.path.join(profile_path, lock_name)
        try:
            if os.path.lexists(lock_path):
                os.remove(lock_path)
        except OSError as e:
            print(f"   [Warning] Could not remove stale lock {lock_name}: {e}")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f"Error starting Chrome: {e}")
        return

    try:
        driver.get("https://pantip.com/login")
        time.sleep(1)

        if "login" in driver.current_url:
            input(">>> Please Login and press [Enter] <<<")

        if mode == "find":
            run_find_mode(driver, max_topics)

        elif mode == "send":
            run_send_mode(driver, max_topics)
        else:
            print("Usage: python pantip_addcomment.py [find <number of topics> | send]")
    finally:
        try:
            driver.quit()
        except Exception:
            pass
    
if __name__ == "__main__":
    main()
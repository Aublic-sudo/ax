import requests
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

# Function to decrypt download links
def decrypt_link(encrypted_link):
    try:
        key = "638udh3829162018".encode("utf8")
        iv = "fedcba9876543210".encode("utf8")
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = b64decode(encrypted_link)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return plaintext.decode()
    except Exception as e:
        print(f"Error decrypting: {e}")
        return None

# Main function to fetch and save video links
def fetch_and_save_links(token):
    # Headers with token
    headers = {
        "Authorization": token,
        "User-Agent": "okhttp/4.9.1",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Cloudscraper session
    scraper = cloudscraper.create_scraper()

    # Fetch user courses
    courses_url = "https://rgvikramjeetapi.classx.co.in/get/mycourse"
    res = scraper.get(courses_url, headers=headers)
    if res.status_code != 200:
        print("Error: Could not fetch courses.")
        return

    courses = res.json().get('data', [])
    if not courses:
        print("No courses found.")
        return

    # Display available courses and ask for selection
    print("Available courses:")
    for i, course in enumerate(courses):
        print(f"{i + 1}. {course['course_name']} (ID: {course['id']})")

    # Ask user to select a course
    course_choice = int(input("Enter the course number: ")) - 1
    selected_course = courses[course_choice]
    course_id = selected_course['id']
    print(f"Selected Course: {selected_course['course_name']}")

    # Fetch subjects for the selected course
    subjects_url = f"https://rgvikramjeetapi.classx.co.in/get/allsubjectfrmlivecourseclass?courseid={course_id}"
    res_subjects = scraper.get(subjects_url, headers=headers)
    if res_subjects.status_code != 200:
        print("Error: Could not fetch subjects.")
        return

    subjects = res_subjects.json().get('data', [])
    if not subjects:
        print("No subjects found for the selected course.")
        return

    # Display available subjects and ask for selection
    print("\nAvailable subjects:")
    for i, subject in enumerate(subjects):
        print(f"{i + 1}. {subject['subject_name']} (ID: {subject['id']})")

    # Ask user to select a subject
    subject_choice = int(input("Enter the subject number: ")) - 1
    selected_subject = subjects[subject_choice]
    subject_id = selected_subject['id']
    print(f"Selected Subject: {selected_subject['subject_name']}")

    # Fetch topics for the selected subject
    topic_url = f"https://rgvikramjeetapi.classx.co.in/get/alltopicfrmlivecourseclass?courseid={course_id}&subjectid={subject_id}"
    res_topics = scraper.get(topic_url, headers=headers)
    if res_topics.status_code != 200:
        print("Error: Could not fetch topics.")
        return

    topics = res_topics.json().get('data', [])
    
    # Open file to save the links
    with open(f"download_links_{course_id}_{subject_id}.txt", "w") as file:
        for topic in topics:
            topic_id = topic["topicid"]
            topic_name = topic["topic_name"]
            print(f"Processing Topic: {topic_name} (ID: {topic_id})")

            # Get download links for the topic
            topic_details_url = f"https://rgvikramjeetapi.classx.co.in/get/livecourseclassbycoursesubtopconceptapiv3?topicid={topic_id}&start=-1&conceptid=1&courseid={course_id}&subjectid={subject_id}"
            res4 = scraper.get(topic_details_url, headers=headers)

            if res4.status_code != 200:
                print(f"Error: Could not fetch video links for {topic_name}. Skipping...")
                continue

            video_data = res4.json().get("data", [])
            for video in video_data:
                title = video["Title"]
                encrypted_link = video.get("download_link") or video.get("pdf_link")

                if encrypted_link:
                    decrypted_url = decrypt_link(encrypted_link)
                    if decrypted_url:
                        print(f"Saving: {title} -> {decrypted_url}")
                        file.write(f"{title}: {decrypted_url}\n")

    print("✅ Links saved to file.")

# Example Usage
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjExMjM4MzciLCJlbWFpbCI6Im1yc2luZ2hzaW5naDkzN0BnbWFpbC5jb20iLCJ0aW1lc3RhbXAiOjE3Mzc4Nzg0NDEsInRlbmFudFR5cGUiOiJ1c2VyIiwidGVuYW50TmFtZSI6IiIsInRlbmFudElkIjoiIiwiZGlzcG9zYWJsZSI6ZmFsc2V9.2fstkzw-Obb-u5lTKmt7jGMfTUiwRcowhw_2RhbX4jI:1123837@MadXABhi_Robot"

fetch_and_save_links(token)  

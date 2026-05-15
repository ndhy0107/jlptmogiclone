import time
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ===== CẤU HÌNH =====
EMAIL = "ndhy0107@gmail.com"  # Thay bằng email đăng nhập
PASSWORD = "susu1783"  # Thay bằng mật khẩu

# URL danh sách đề thi N2
LIST_URL = "https://jlptmogi.com/giai-de-sach/n2/fb_mojigoi_n2"

def login(driver):
    """Đăng nhập vào jlptmogi.com"""
    print("\n🔐 Đang đăng nhập...")
    
    # Mở trang chủ
    driver.get("https://jlptmogi.com/")
    time.sleep(2)
    
    # Click nút mở popup đăng nhập
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.content-wrapper > header > nav > div > div.navbar-other.w-100.d-flex.ms-auto > ul > li:nth-child(1) > a"))
    )
    login_btn.click()
    time.sleep(1)
    
    # Nhập email
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#modal-signin input[type='email'], #modal-signin input[type='text']"))
    )
    email_input.clear()
    email_input.send_keys(EMAIL)
    
    # Nhập password
    password_input = driver.find_element(By.CSS_SELECTOR, "#modal-signin input[type='password']")
    password_input.clear()
    password_input.send_keys(PASSWORD)
    
    # Click nút đăng nhập
    submit_btn = driver.find_element(By.CSS_SELECTOR, "#modal-signin > div > div > div > form > a")
    submit_btn.click()
    time.sleep(3)
    
    # Kiểm tra đăng nhập thành công
    try:
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "modal-signin"))
        )
        print("✅ Đăng nhập thành công!")
        return True
    except:
        print("❌ Đăng nhập thất bại!")
        return False

def get_all_exam_links(driver):
    """Lấy tất cả link đề thi từ trang danh sách"""
    print(f"\n📋 Đang truy cập: {LIST_URL}")
    driver.get(LIST_URL)
    time.sleep(3)
    
    # Chờ bảng tải xong
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
        print("✅ Đã tải danh sách đề thi")
    except TimeoutException:
        print("❌ Không thể tải danh sách đề thi")
        return []
    
    # Tìm tất cả các thẻ a có href chứa "/jlpt?dethi="
    exam_links = []
    
    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        print(f"📊 Tìm thấy {len(rows)} dòng trong bảng")
        
        for idx, row in enumerate(rows, 1):
            try:
                link_elem = row.find_element(By.CSS_SELECTOR, "td.item_baihoc div a")
                href = link_elem.get_attribute("href")
                text = link_elem.text.strip()
                
                if href and "dethi=" in href:
                    exam_links.append({
                        "index": idx,
                        "title": text if text else f"Đề {idx}",
                        "url": href
                    })
                    print(f"  ✅ {idx}. {text}")
            except:
                continue
    except Exception as e:
        print(f"⚠️ Lỗi khi parse bảng: {e}")
    
    print(f"\n📚 Tổng cộng tìm thấy {len(exam_links)} đề thi")
    return exam_links

def click_lam_bai_button(driver):
    """Click vào nút 'Làm bài' trước khi vào đề"""
    try:
        lam_bai_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#section_thithu > div.content_thithu > div.intro_phanthi.intro_phanthi1 > div > div.btn_action > div.bd_lambai"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", lam_bai_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", lam_bai_btn)
        print("  ✅ Đã click nút 'Làm bài'")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"  ⚠️ Không tìm thấy nút 'Làm bài': {e}")
        return False

def get_all_questions_with_options(driver):
    """Lấy tất cả câu hỏi và đáp án từ cấu trúc HTML"""
    questions = []
    
    # Tìm tất cả các khối content_ques
    content_ques_list = driver.find_elements(By.CSS_SELECTOR, "div.content_ques")
    
    if not content_ques_list:
        print("    ❌ Không tìm thấy khối câu hỏi nào")
        return questions
    
    for idx, content_ques in enumerate(content_ques_list, 1):
        try:
            # Lấy câu hỏi (trong div.name_ques > div.txt_ques)
            question_text = ""
            try:
                name_ques = content_ques.find_element(By.CSS_SELECTOR, "div.name_ques div.txt_ques")
                question_text = name_ques.text.strip()
            except:
                try:
                    name_ques = content_ques.find_element(By.CSS_SELECTOR, "div.name_ques")
                    question_text = name_ques.text.strip()
                except:
                    question_text = ""
            
            # Lấy tất cả đáp án (trong div.thithu_ans > div.item_ans)
            options = []
            answer_items = content_ques.find_elements(By.CSS_SELECTOR, "div.thithu_ans div.item_ans")
            
            for opt_idx, item_ans in enumerate(answer_items, 1):
                try:
                    # Lấy số thứ tự đáp án
                    sel_num = item_ans.find_element(By.CSS_SELECTOR, "div.sel_num").text.strip()
                    
                    # Lấy nội dung đáp án
                    sel_txt = item_ans.find_element(By.CSS_SELECTOR, "div.sel_txt").text.strip()
                    
                    options.append({
                        "number": sel_num,
                        "text": sel_txt
                    })
                except Exception as e:
                    print(f"      ⚠️ Lỗi lấy đáp án {opt_idx} câu {idx}: {e}")
            
            # Thêm câu hỏi vào danh sách
            questions.append({
                "question": question_text,
                "options": options
            })
            
        except Exception as e:
            print(f"    ❌ Lỗi câu {idx}: {e}")
            questions.append({
                "question": f"Lỗi khi crawl: {e}",
                "options": []
            })
    
    return questions

def crawl_exam_questions(driver, exam_info, exam_id):
    """Crawl nội dung câu hỏi và đáp án của đề thi"""
    print(f"\n📖 Đang crawl: {exam_info['title']}")
    driver.get(exam_info['url'])
    time.sleep(3)
    
    # Click nút "Làm bài"
    if not click_lam_bai_button(driver):
        print(f"  ⚠️ Không thể vào đề thi: {exam_info['title']}")
        return None
    
    # Chờ câu hỏi load
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.content_ques"))
        )
        print("  ✅ Đã tải câu hỏi")
    except TimeoutException:
        print(f"  ⚠️ Không tìm thấy câu hỏi cho {exam_info['title']}")
        return None
    
    # Lấy tất cả câu hỏi và đáp án
    questions = get_all_questions_with_options(driver)
    
    if not questions:
        print(f"  ⚠️ Không tìm thấy câu hỏi nào")
        return None
    
    return {
        "de_id": exam_id,
        "de_name": exam_info['title'],
        "de_url": exam_info['url'],
        "total_questions": len(questions),
        "questions": questions
    }

def save_all_to_json(all_exams, filename="n2_all_exams.json"):
    """Lưu tất cả đề thi vào 1 file JSON duy nhất"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_exams, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Đã lưu toàn bộ dữ liệu vào: {filename}")
    return filename

def main():
    print("="*60)
    print("🚀 CRAWL TOÀN BỘ ĐỀ THI N2 - JLPT MOGI")
    print("="*60)
    
    # Khởi tạo driver
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    all_exams = []
    total_questions_all = 0
    
    try:
        # Đăng nhập
        if not login(driver):
            print("❌ Không thể đăng nhập, dừng chương trình")
            return
        
        # Lấy danh sách đề thi
        exam_links = get_all_exam_links(driver)
        
        if not exam_links:
            print("❌ Không tìm thấy đề thi nào")
            return
        
        # Crawl toàn bộ đề thi
        print(f"\n{'='*60}")
        print(f"🎯 BẮT ĐẦU CRAWL {len(exam_links)} ĐỀ THI")
        print(f"{'='*60}")
        
        for idx, exam_info in enumerate(exam_links, 1):
            # Tạo ID cho đề (de_01, de_02, ...)
            exam_id = f"de_{idx:02d}"
            
            print(f"\n--- Đề {idx}/{len(exam_links)} | ID: {exam_id} ---")
            print(f"📌 Tên: {exam_info['title']}")
            
            # Crawl câu hỏi
            exam_data = crawl_exam_questions(driver, exam_info, exam_id)
            
            if exam_data:
                all_exams.append(exam_data)
                total_questions_all += exam_data['total_questions']
                print(f"  ✅ Thành công! Số câu hỏi: {exam_data['total_questions']}")
            else:
                print(f"  ⚠️ Bỏ qua đề {exam_info['title']}")
            
            # Chờ giữa các đề để tránh bị chặn
            time.sleep(3)
        
        # Lưu toàn bộ vào 1 file JSON
        if all_exams:
            save_all_to_json(all_exams)
            
            # LOG KẾT QUẢ
            print("\n" + "="*60)
            print("📊 THỐNG KÊ DỮ LIỆU CRAWL")
            print("="*60)
            print(f"✅ Số đề thi đã crawl thành công: {len(all_exams)}/{len(exam_links)}")
            print(f"📝 Tổng số câu hỏi đã crawl: {total_questions_all}")
            print(f"📈 Trung bình mỗi đề: {total_questions_all/len(all_exams):.1f} câu")
            print("="*60)
            
            # Hiển thị chi tiết từng đề
            print("\n📋 CHI TIẾT TỪNG ĐỀ:")
            for exam in all_exams:
                print(f"  - {exam['de_id']}: {exam['de_name']} ({exam['total_questions']} câu)")
        else:
            print("\n❌ Không có đề thi nào được crawl thành công!")
        
        print("\n⏸ Trình duyệt sẽ đóng sau 10 giây...")
        time.sleep(10)
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")
        driver.save_screenshot("error_screenshot.png")
        print("📸 Đã lưu ảnh lỗi: error_screenshot.png")
        
    finally:
        driver.quit()
        print("🔒 Đã đóng trình duyệt")

if __name__ == "__main__":
    main()
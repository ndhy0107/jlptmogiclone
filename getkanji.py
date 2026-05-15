import json
import re

# Định nghĩa khoảng Unicode của Kanji (mở rộng thêm một số Kanji hiếm)
KANJI_PATTERN = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')  # Bao gồm cả Kanji mở rộng

def extract_kanji(text):
    """Trích xuất TẤT CẢ Kanji từ câu hỏi, giữ nguyên thứ tự, nối bằng dấu phẩy"""
    kanji_list = KANJI_PATTERN.findall(text)
    
    # Bỏ trùng lặp nhưng GIỮ NGUYÊN thứ tự xuất hiện
    seen = set()
    unique_kanji = []
    for k in kanji_list:
        if k not in seen:
            seen.add(k)
            unique_kanji.append(k)
    
    # Nối bằng dấu phẩy
    return ','.join(unique_kanji)

def extract_kanji_with_details(text):
    """Trích xuất Kanji kèm thông tin chi tiết"""
    kanji_list = KANJI_PATTERN.findall(text)
    seen = set()
    unique_kanji = []
    positions = []
    
    for idx, k in enumerate(kanji_list):
        positions.append(f"{k}@{idx}")
        if k not in seen:
            seen.add(k)
            unique_kanji.append(k)
    
    return {
        'kanji': ','.join(unique_kanji),
        'all_kanji_with_position': positions,
        'total_kanji_found': len(kanji_list),
        'unique_kanji_count': len(unique_kanji)
    }

def test_extraction():
    """Test thử với câu hỏi mẫu"""
    test_text = "【1021】同点のため、試合は３０分（延長）されることになった。"
    result = extract_kanji_with_details(test_text)
    
    print("="*60)
    print("🧪 TEST TRÍCH XUẤT KANJI")
    print("="*60)
    print(f"Câu hỏi: {test_text}")
    print(f"\n📊 Kết quả:")
    print(f"   - Kanji (dạng chuỗi): {result['kanji']}")
    print(f"   - Tất cả Kanji tìm thấy: {result['all_kanji_with_position']}")
    print(f"   - Tổng số Kanji trong câu: {result['total_kanji_found']}")
    print(f"   - Số Kanji duy nhất: {result['unique_kanji_count']}")
    print("="*60)

def process_json_file(input_file, output_file):
    """Đọc file JSON, thêm trường kanji cho mỗi câu hỏi"""
    
    print(f"📖 Đang đọc file: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_questions = 0
    total_kanji_found = 0
    
    for exam in data:
        for question in exam.get('questions', []):
            question_text = question.get('question', '')
            
            # Trích xuất Kanji
            result = extract_kanji_with_details(question_text)
            kanji_string = result['kanji']
            
            # Thêm trường kanji vào câu hỏi
            question['kanji'] = kanji_string
            # Tùy chọn: thêm thêm thông tin chi tiết
            # question['kanji_count'] = result['unique_kanji_count']
            # question['total_kanji_in_sentence'] = result['total_kanji_found']
            
            total_questions += 1
            total_kanji_found += result['unique_kanji_count']
    
    print(f"\n✅ Đã xử lý {total_questions} câu hỏi")
    print(f"📊 Tổng số Kanji duy nhất đã trích xuất: {total_kanji_found}")
    print(f"📊 Trung bình Kanji/câu: {total_kanji_found/total_questions:.1f}")
    
    # Lưu file mới
    print(f"💾 Đang lưu vào: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("✅ Hoàn thành!")
    return data

def preview_changes(input_file, sample_count=5):
    """Xem trước thay đổi với một số câu mẫu"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("\n📋 XEM TRƯỚC THAY ĐỔI (5 câu đầu):")
    print("="*70)
    
    count = 0
    for exam in data:
        for question in exam.get('questions', []):
            if count >= sample_count:
                break
            question_text = question.get('question', '')
            kanji = extract_kanji(question_text)
            print(f"\n📝 {count+1}. Câu hỏi: {question_text}")
            print(f"🔤 Kanji    : {kanji}")
            print("-"*70)
            count += 1
        if count >= sample_count:
            break

if __name__ == "__main__":
    # Test trước với câu mẫu
    test_extraction()
    
    INPUT_FILE = 'n2_all_exams.json'
    OUTPUT_FILE = 'n2_all_exams_with_kanji.json'
    
    # Xem trước 5 câu từ file thật
    preview_changes(INPUT_FILE, 5)
    
    # Xác nhận
    print("\n" + "="*60)
    confirm = input("👉 Bạn có muốn xử lý toàn bộ file? (y/n): ")
    
    if confirm.lower() == 'y':
        process_json_file(INPUT_FILE, OUTPUT_FILE)
        print("\n🎉 XONG! File mới đã được tạo: " + OUTPUT_FILE)
    else:
        print("❌ Đã hủy")
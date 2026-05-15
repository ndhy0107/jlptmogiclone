from flask import Flask, render_template, jsonify, request
import json
import os
import random

app = Flask(__name__)

# ===== CẤU HÌNH ĐƯỜNG DẪN =====
# Lấy đường dẫn tuyệt đối đến thư mục hiện tại
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, 'n2_all_exams.json')

# ===== HÀM ĐỌC/GHI FILE JSON =====
def load_exam_data():
    """Đọc dữ liệu từ file JSON"""
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file: {JSON_FILE}")
        return []
    except Exception as e:
        print(f"❌ Lỗi đọc file: {e}")
        return []

def save_exam_data(data):
    """Lưu dữ liệu vào file JSON"""
    try:
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Lỗi lưu file: {e}")
        return False

def get_all_questions():
    """Lấy tất cả câu hỏi từ các đề"""
    exam_data = load_exam_data()
    all_questions = []
    
    for exam in exam_data:
        for idx, question in enumerate(exam.get('questions', [])):
            # Thêm countreviewed nếu chưa có
            if 'countreviewed' not in question:
                question['countreviewed'] = 0
            # Thêm correct_answer nếu chưa có
            if 'correct_answer' not in question:
                question['correct_answer'] = ''
            # Thêm explanation nếu chưa có
            if 'explanation' not in question:
                question['explanation'] = ''
            
            all_questions.append({
                'de_id': exam.get('de_id'),
                'de_name': exam.get('de_name'),
                'question': question.get('question'),
                'options': question.get('options', []),
                'explanation': question.get('explanation', ''),
                'correct_answer': question.get('correct_answer', ''),
                'countreviewed': question.get('countreviewed', 0),
                'exam_index': exam_data.index(exam),
                'question_index': idx,
                'kanji': question.get('kanji', ''), 
            })
    
    return all_questions, exam_data

# ===== API ROUTES =====
@app.route('/')
def index():
    """Trang chủ"""
    return render_template('index.html')

@app.route('/api/questions')
def get_questions():
    """API lấy danh sách câu hỏi"""
    questions, _ = get_all_questions()
    return jsonify({
        'total': len(questions),
        'questions': questions
    })

@app.route('/api/save-explanation', methods=['POST'])
def save_explanation():
    """API lưu giải thích và đáp án đúng cho câu hỏi"""
    try:
        data = request.json
        question_index = data.get('question_index')
        explanation = data.get('explanation', '')
        correct_answer = data.get('correct_answer', '')
        
        exam_data = load_exam_data()
        questions, _ = get_all_questions()
        
        if 0 <= question_index < len(questions):
            q = questions[question_index]
            exam_idx = q['exam_index']
            q_idx = q['question_index']
            
            exam_data[exam_idx]['questions'][q_idx]['explanation'] = explanation
            exam_data[exam_idx]['questions'][q_idx]['correct_answer'] = correct_answer
            
            if save_exam_data(exam_data):
                return jsonify({'success': True, 'message': 'Đã lưu giải thích và đáp án đúng!'})
            else:
                return jsonify({'success': False, 'message': 'Lỗi lưu file'})
        else:
            return jsonify({'success': False, 'message': 'Không tìm thấy câu hỏi'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/save-review', methods=['POST'])
def save_review():
    """API lưu số lần review cho câu hỏi"""
    try:
        data = request.json
        question_index = data.get('question_index')
        countreviewed = data.get('countreviewed', 0)
        
        exam_data = load_exam_data()
        questions, _ = get_all_questions()
        
        if 0 <= question_index < len(questions):
            q = questions[question_index]
            exam_idx = q['exam_index']
            q_idx = q['question_index']
            
            exam_data[exam_idx]['questions'][q_idx]['countreviewed'] = countreviewed
            
            if save_exam_data(exam_data):
                return jsonify({'success': True, 'message': f'Đã lưu review: {countreviewed}/5'})
            else:
                return jsonify({'success': False, 'message': 'Lỗi lưu file'})
        else:
            return jsonify({'success': False, 'message': 'Không tìm thấy câu hỏi'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/next-question', methods=['POST'])
def get_next_question():
    """Lấy câu hỏi tiếp theo dựa trên priority (ưu tiên câu có countreviewed thấp)"""
    try:
        questions, _ = get_all_questions()
        
        if not questions:
            return jsonify({'success': False, 'message': 'Không có câu hỏi'})
        
        # Lọc các câu có countreviewed < 3 (ưu tiên ôn tập)
        low_review = [i for i, q in enumerate(questions) if q['countreviewed'] < 3]
        
        if low_review:
            next_idx = random.choice(low_review)
        else:
            # Nếu tất cả đã review >= 3, chọn random toàn bộ
            next_idx = random.randint(0, len(questions) - 1)
        
        return jsonify({
            'success': True,
            'next_index': next_idx
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ===== CHẠY SERVER =====
if __name__ == '__main__':
    print("🚀 Khởi động Flask server...")
    print(f"📍 Đường dẫn file JSON: {JSON_FILE}")
    print(f"📊 Tổng số câu hỏi: {len(get_all_questions()[0])}")
    print("="*50)
    app.run(host="0.0.0.0", port=8080)
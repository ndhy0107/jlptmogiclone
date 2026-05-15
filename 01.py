import time
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://jlptmogi.com/")
time.sleep(3)

print("=== TÌM TẤT CẢ CÁC NÚT/THẺ CÓ CHỨA 'ĐĂNG NHẬP' ===\n")

# Cách 1: Tìm bằng link text
try:
    elements = driver.find_elements(By.LINK_TEXT, "ĐĂNG NHẬP")
    print(f"1. LINK_TEXT 'ĐĂNG NHẬP': tìm thấy {len(elements)} phần tử")
    for el in elements:
        print(f"   - Tag: {el.tag_name}, Class: {el.get_attribute('class')}")
except Exception as e:
    print(f"1. LINK_TEXT lỗi: {e}")

# Cách 2: Tìm bằng partial link text
try:
    elements = driver.find_elements(By.PARTIAL_LINK_TEXT, "ĐĂNG NHẬP")
    print(f"2. PARTIAL_LINK_TEXT 'ĐĂNG NHẬP': tìm thấy {len(elements)} phần tử")
    for el in elements:
        print(f"   - Tag: {el.tag_name}, Class: {el.get_attribute('class')}")
except Exception as e:
    print(f"2. PARTIAL_LINK_TEXT lỗi: {e}")

# Cách 3: Tìm bằng XPath với text chính xác
try:
    elements = driver.find_elements(By.XPATH, "//*[text()='ĐĂNG NHẬP']")
    print(f"3. XPath text()='ĐĂNG NHẬP': tìm thấy {len(elements)} phần tử")
    for el in elements:
        print(f"   - Tag: {el.tag_name}, Class: {el.get_attribute('class')}")
except Exception as e:
    print(f"3. XPath lỗi: {e}")

# Cách 4: Tìm bằng XPath với contains
try:
    elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'ĐĂNG NHẬP')]")
    print(f"4. XPath contains 'ĐĂNG NHẬP': tìm thấy {len(elements)} phần tử")
    for el in elements:
        print(f"   - Tag: {el.tag_name}, Class: {el.get_attribute('class')}, HTML: {el.get_attribute('outerHTML')[:200]}")
except Exception as e:
    print(f"4. XPath lỗi: {e}")

# Cách 5: Tìm tất cả thẻ a có class 'nav-link'
try:
    elements = driver.find_elements(By.CSS_SELECTOR, "a.nav-link")
    print(f"\n5. CSS a.nav-link: tìm thấy {len(elements)} phần tử")
    for el in elements:
        print(f"   - Text: {el.text}, Class: {el.get_attribute('class')}, data-bs-toggle: {el.get_attribute('data-bs-toggle')}")
except Exception as e:
    print(f"5. CSS lỗi: {e}")

# Cách 6: Tìm tất cả thẻ có data-bs-toggle='modal'
try:
    elements = driver.find_elements(By.CSS_SELECTOR, "[data-bs-toggle='modal']")
    print(f"\n6. CSS [data-bs-toggle='modal']: tìm thấy {len(elements)} phần tử")
    for el in elements:
        print(f"   - Text: {el.text}, Tag: {el.tag_name}, data-bs-target: {el.get_attribute('data-bs-target')}")
except Exception as e:
    print(f"6. CSS lỗi: {e}")

# In ra toàn bộ nội dung trang để kiểm tra
print("\n=== KIỂM TRA NỘI DUNG TRANG ===")
page_text = driver.find_element(By.TAG_NAME, "body").text
if "ĐĂNG NHẬP" in page_text:
    print("✅ Tìm thấy chữ 'ĐĂNG NHẬP' trong nội dung trang")
else:
    print("❌ Không tìm thấy chữ 'ĐĂNG NHẬP' trong nội dung trang")

driver.quit()
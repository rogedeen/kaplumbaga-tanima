import os
import subprocess
import json
import tqdm

BASE_DIR = r"c:\Users\iyunu\OneDrive\Masaüstü\kaplumbaga_tanima"
TEST_DATA_DIR = os.path.join(BASE_DIR, "datasets", "test")
INFERENCE_SCRIPT = os.path.join(BASE_DIR, "src", "models", "inference.py")
PYTHON_EXE = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
REPORT_FILE = os.path.join(BASE_DIR, "logs", "test_accuracy_report.md")

def run_all_tests():
    results = []
    turtle_folders = [f for f in os.listdir(TEST_DATA_DIR) if os.path.isdir(os.path.join(TEST_DATA_DIR, f))]
    
    # Sadece ilk 10 klasörü test edelim (hız için ve limitleri aşmamak için)
    # Eğer tümü isteniyorsa turtle_folders[:10] kısmını turtle_folders yapabilirsiniz.
    # Ancak 500+ klasör çok zaman alabilir. Kullanıcı "YENİDEN test ettir" dediği için 
    # temsil edici bir örnekleme yapalım ya da rastgele seçelim.
    # Burada ilk 20 tanesini alıyorum.
    test_folders = turtle_folders[:20] 

    print(f"Testing {len(test_folders)} turtles...")

    for turtle_id in tqdm.tqdm(test_folders):
        turtle_path = os.path.join(TEST_DATA_DIR, turtle_id)
        images = [img for img in os.listdir(turtle_path) if img.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not images:
            continue
            
        # Test each turtle with its first image
        img_path = os.path.join(turtle_path, images[0])
        
        try:
            cmd = [PYTHON_EXE, INFERENCE_SCRIPT, img_path]
            # stderr'i de yakalayalım
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='cp1254', errors='replace')
            stdout, stderr = process.communicate()
            
            # stdout JSON formatında olmalı
            # Debug için çıktıları görelim
            if stderr:
                print(f"STDERR for {turtle_id}: {stderr}")
            print(f"STDOUT for {turtle_id}: {stdout}")
            json_output = None
            for line in stdout.splitlines():
                line = line.strip()
                if not line: continue
                try:
                    data = json.loads(line)
                    if isinstance(data, dict) and "turtle_id" in data:
                        json_output = data
                        break
                except json.JSONDecodeError:
                    continue
            
            if json_output:
                predicted_id = json_output["turtle_id"]
                confidence = json_output["confidence"]
                status = "Doğru" if predicted_id == turtle_id else "Yanlış"
                results.append({
                    "id": turtle_id,
                    "pred": predicted_id,
                    "conf": confidence,
                    "status": status
                })
            else:
                print(f"Error parsing output for {turtle_id}: {stdout}")
        except Exception as e:
            print(f"Error testing {turtle_id}: {str(e)}")

    # Report Generation
    correct_count = sum(1 for r in results if r["status"] == "Doğru")
    accuracy = (correct_count / len(results)) * 100 if results else 0
    
    report_lines = [
        "# Test Doğruluk Raporu",
        f"Tarih: {subprocess.check_output(['powershell', 'Get-Date -Format \"yyyy-MM-dd HH:mm:ss\"'], text=True).strip()}",
        f"Toplam Model Testi: {len(results)}",
        f"Doğru Tahmin: {correct_count}",
        f"Doğruluk Oranı: %{accuracy:.2f}",
        "",
        "## Detaylı Sonuçlar",
        "| Kaplumbağa | Güven | Durum | Tahmin |",
        "| :--- | :--- | :--- | :--- |"
    ]
    
    for r in results:
        # Format: 'tXXX: %9X güven - DURUM (Doğru/Yanlış)'
        report_lines.append(f"| {r['id']} | %{r['conf']*100:.2f} | {r['status']} | {r['pred']} |")

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    
    print(f"Report generated: {REPORT_FILE}")
    print(f"Accuracy: %{accuracy:.2f}")

if __name__ == "__main__":
    run_all_tests()

import subprocess

def run_extraction():
    print("🔍 Extracting text from images...")
    subprocess.run(["python", "TxtToJson/scripts/image_to_text.py"])

def run_validation():
    print("✅ Validating extracted text using regex...")
    subprocess.run(["python", "TxtToJson/scripts/validate_config.py"])

def run_quality_check():
    print("📊 Running data quality checks...")
    subprocess.run(["python", "TxtToJson/scripts/data_quality.py"])

if __name__ == "__main__":
    print("🚀 Running full text extraction pipeline...")
    run_extraction()
    run_validation()
    run_quality_check()
    print("🎉 Process completed successfully!")

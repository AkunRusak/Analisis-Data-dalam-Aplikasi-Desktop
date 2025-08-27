#!/usr/bin/env python3
"""
Quick Build Script - Simple PyInstaller wrapper
Solusi cepat untuk build aplikasi Gantt Chart tanpa parameter kompleks
"""

import os
import sys
import subprocess
import shutil

def check_file_exists():
    """Cek apakah file utama ada"""
    if not os.path.exists('GanttAnalysisApp.py'):
        print("❌ Error: File GanttAnalysisApp.py tidak ditemukan!")
        print("   Pastikan file ini berada di direktori yang sama.")
        return False
    return True

def install_requirements():
    """Install dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        print("✅ PyInstaller installed")
        
        # Install other requirements if file exists
        if os.path.exists('requirements.txt'):
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Requirements installed")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def cleanup_previous_build():
    """Bersihkan build sebelumnya"""
    folders_to_clean = ['build', 'dist']
    files_to_clean = ['*.spec']
    
    for folder in folders_to_clean:
        if os.path.exists(folder):
            print(f"🧹 Cleaning {folder}...")
            shutil.rmtree(folder)
    
    # Clean spec files
    import glob
    for spec_file in glob.glob('*.spec'):
        os.remove(spec_file)
        print(f"🧹 Removed {spec_file}")

def build_single_file():
    """Build single file executable - PALING SEDERHANA"""
    print("\n🔨 Building single file executable...")
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=GanttAnalysisApp',
        'GanttAnalysisApp.py'
    ]
    
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            print("📁 Output: dist/GanttAnalysisApp.exe")
            return True
        else:
            print("❌ Build failed!")
            print("Error output:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during build: {e}")
        return False

def build_with_hidden_imports():
    """Build dengan hidden imports untuk dependencies yang mungkin tidak terdeteksi"""
    print("\n🔨 Building with explicit imports...")
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=GanttAnalysisApp',
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=matplotlib',
        '--hidden-import=PyQt6',
        '--hidden-import=matplotlib.backends.backend_qt5agg',
        '--hidden-import=matplotlib.figure',
        '--hidden-import=matplotlib.dates',
        'GanttAnalysisApp.py'
    ]
    
    try:
        print(f"Running: {' '.join(cmd[:5])}... (dengan hidden imports)")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            print("📁 Output: dist/GanttAnalysisApp.exe")
            return True
        else:
            print("❌ Build failed!")
            print("Error output:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during build: {e}")
        return False

def build_directory_mode():
    """Build directory mode - lebih kompatibel"""
    print("\n🔨 Building directory mode...")
    
    cmd = [
        'pyinstaller',
        '--onedir',
        '--windowed',
        '--name=GanttAnalysisApp',
        'GanttAnalysisApp.py'
    ]
    
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            print("📁 Output: dist/GanttAnalysisApp/GanttAnalysisApp.exe")
            return True
        else:
            print("❌ Build failed!")
            print("Error output:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during build: {e}")
        return False

def main():
    """Main function"""
    print("="*50)
    print("🚀 QUICK BUILD SCRIPT")
    print("   Gantt Chart Analysis App")
    print("="*50)
    
    # Step 1: Check file
    if not check_file_exists():
        input("Press Enter to exit...")
        return
    
    # Step 2: Install requirements
    print("\n📋 Step 1: Installing requirements...")
    if not install_requirements():
        input("Press Enter to exit...")
        return
    
    # Step 3: Clean previous builds
    print("\n📋 Step 2: Cleaning previous builds...")
    cleanup_previous_build()
    
    # Step 4: Choose build method
    print("\n📋 Step 3: Choose build method:")
    print("1. Simple build (quick)")
    print("2. Build with imports (recommended)")
    print("3. Directory mode (most compatible)")
    print("4. Try all methods")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    success = False
    
    if choice == '1':
        success = build_single_file()
    elif choice == '2':
        success = build_with_hidden_imports()
    elif choice == '3':
        success = build_directory_mode()
    elif choice == '4':
        print("\n🔄 Trying all methods...")
        success = (build_single_file() or 
                  build_with_hidden_imports() or 
                  build_directory_mode())
    else:
        print("❌ Invalid choice!")
        input("Press Enter to exit...")
        return
    
    # Results
    if success:
        print("\n🎉 BUILD COMPLETED SUCCESSFULLY!")
        print("\n📁 Check the 'dist' folder for your executable")
        print("💡 You can now distribute the executable to other computers")
        
        # Show what was built
        if os.path.exists('dist/GanttAnalysisApp.exe'):
            size = os.path.getsize('dist/GanttAnalysisApp.exe') // (1024*1024)
            print(f"📄 Single file: dist/GanttAnalysisApp.exe ({size} MB)")
        
        if os.path.exists('dist/GanttAnalysisApp/GanttAnalysisApp.exe'):
            print(f"📁 Directory: dist/GanttAnalysisApp/")
            
    else:
        print("\n💥 BUILD FAILED!")
        print("\n🔧 Try these solutions:")
        print("1. Update PyInstaller: pip install --upgrade pyinstaller")
        print("2. Install Visual C++ Redistributable (Windows)")
        print("3. Run with --console flag to see detailed errors")
        print("4. Check if all dependencies are installed")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
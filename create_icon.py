#!/usr/bin/env python3
"""
Create a cool modern wellness app icon
"""

import os
import subprocess
from pathlib import Path

def create_wellness_icon_svg():
    """Create a modern wellness icon in SVG format"""
    
    # Modern wellness icon with geometric design
    svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="1024" height="1024" viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Main gradient -->
    <radialGradient id="mainGradient" cx="50%" cy="30%" r="70%">
      <stop offset="0%" style="stop-color:#4FC3F7;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#29B6F6;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0288D1;stop-opacity:1" />
    </radialGradient>
    
    <!-- Accent gradient -->
    <radialGradient id="accentGradient" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#66BB6A;stop-opacity:0.9" />
      <stop offset="100%" style="stop-color:#43A047;stop-opacity:0.7" />
    </radialGradient>
    
    <!-- Inner glow -->
    <radialGradient id="innerGlow" cx="50%" cy="50%" r="40%">
      <stop offset="0%" style="stop-color:#FFFFFF;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#FFFFFF;stop-opacity:0" />
    </radialGradient>
    
    <!-- Shadow -->
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="#000000" flood-opacity="0.2"/>
    </filter>
  </defs>
  
  <!-- Background circle -->
  <circle cx="512" cy="512" r="480" fill="url(#mainGradient)" filter="url(#shadow)"/>
  
  <!-- Main wellness symbol - abstract lotus/zen design -->
  <g transform="translate(512,512)">
    <!-- Central circle -->
    <circle cx="0" cy="0" r="80" fill="url(#innerGlow)"/>
    
    <!-- Lotus petals/wellness curves -->
    <g opacity="0.8">
      <!-- Top curves -->
      <path d="M -120,-60 Q 0,-200 120,-60 Q 0,-100 -120,-60 Z" fill="url(#accentGradient)" opacity="0.7"/>
      <path d="M -80,-80 Q 0,-160 80,-80 Q 0,-120 -80,-80 Z" fill="#FFFFFF" opacity="0.2"/>
      
      <!-- Side curves -->
      <g transform="rotate(120)">
        <path d="M -120,-60 Q 0,-200 120,-60 Q 0,-100 -120,-60 Z" fill="url(#accentGradient)" opacity="0.7"/>
        <path d="M -80,-80 Q 0,-160 80,-80 Q 0,-120 -80,-80 Z" fill="#FFFFFF" opacity="0.2"/>
      </g>
      
      <g transform="rotate(240)">
        <path d="M -120,-60 Q 0,-200 120,-60 Q 0,-100 -120,-60 Z" fill="url(#accentGradient)" opacity="0.7"/>
        <path d="M -80,-80 Q 0,-160 80,-80 Q 0,-120 -80,-80 Z" fill="#FFFFFF" opacity="0.2"/>
      </g>
    </g>
    
    <!-- Center wellness dot -->
    <circle cx="0" cy="0" r="40" fill="#FFFFFF" opacity="0.9"/>
    <circle cx="0" cy="0" r="25" fill="url(#accentGradient)"/>
    <circle cx="0" cy="0" r="15" fill="#FFFFFF" opacity="0.6"/>
  </g>
  
  <!-- Subtle outer ring -->
  <circle cx="512" cy="512" r="480" fill="none" stroke="#FFFFFF" stroke-width="4" opacity="0.3"/>
</svg>"""
    
    return svg_content

def create_png_from_svg(svg_content, size, output_path):
    """Convert SVG to PNG at specified size"""
    # Save SVG temporarily
    svg_path = "temp_icon.svg"
    with open(svg_path, 'w') as f:
        f.write(svg_content)
    
    try:
        # Try using rsvg-convert (if available)
        subprocess.run([
            'rsvg-convert', 
            '-w', str(size), 
            '-h', str(size), 
            svg_path, 
            '-o', output_path
        ], check=True, capture_output=True)
        print(f"✅ Created PNG: {output_path} ({size}x{size})")
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # Try using ImageMagick convert
            subprocess.run([
                'convert', 
                '-background', 'transparent',
                '-size', f'{size}x{size}',
                svg_path, 
                output_path
            ], check=True, capture_output=True)
            print(f"✅ Created PNG: {output_path} ({size}x{size})")
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback: Create a simple colored circle using PIL if available
            try:
                from PIL import Image, ImageDraw
                
                # Create a simple gradient circle as fallback
                img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                margin = size // 20
                draw.ellipse([margin, margin, size-margin, size-margin], 
                           fill=(41, 182, 246, 255))  # Material blue
                
                # Add inner circle
                inner_margin = size // 3
                draw.ellipse([inner_margin, inner_margin, size-inner_margin, size-inner_margin], 
                           fill=(102, 187, 106, 200))  # Material green
                
                img.save(output_path, 'PNG')
                print(f"✅ Created fallback PNG: {output_path} ({size}x{size})")
            except ImportError:
                print(f"❌ Could not create PNG for size {size}x{size}. Please install rsvg-convert, ImageMagick, or PIL/Pillow.")
    
    # Clean up temp SVG
    try:
        os.remove(svg_path)
    except:
        pass

def create_icns_file():
    """Create macOS .icns file from PNG images"""
    print("🎨 Creating wellness app icon...")
    
    # Create SVG content
    svg_content = create_wellness_icon_svg()
    
    # Save main SVG file
    with open("wellness_icon.svg", 'w') as f:
        f.write(svg_content)
    print("✅ Created SVG: wellness_icon.svg")
    
    # Create iconset directory
    iconset_dir = "WellnessIcon.iconset"
    os.makedirs(iconset_dir, exist_ok=True)
    
    # Icon sizes required for macOS .icns
    icon_sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png")
    ]
    
    # Generate PNG files
    for size, filename in icon_sizes:
        png_path = os.path.join(iconset_dir, filename)
        create_png_from_svg(svg_content, size, png_path)
    
    # Convert iconset to .icns using macOS iconutil
    try:
        subprocess.run([
            'iconutil', 
            '-c', 'icns', 
            iconset_dir,
            '-o', 'wellness_icon.icns'
        ], check=True)
        print("✅ Created macOS icon: wellness_icon.icns")
        
        # Clean up iconset directory
        import shutil
        shutil.rmtree(iconset_dir)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create .icns file: {e}")
        print("The PNG files are available in the iconset directory for manual conversion.")
        return False
    except FileNotFoundError:
        print("❌ iconutil not found. Are you running on macOS?")
        print("The PNG files are available in the iconset directory.")
        return False

if __name__ == "__main__":
    success = create_icns_file()
    
    if success:
        print("\n🎉 Icon creation completed successfully!")
        print("📁 Files created:")
        print("  - wellness_icon.svg (vector source)")
        print("  - wellness_icon.icns (macOS app icon)")
    else:
        print("\n⚠️  Icon creation partially completed.")
        print("You can manually convert the PNG files to .icns format.")
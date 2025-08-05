#!/usr/bin/env python3
"""
Script d'optimisation d'images SIMPLE - Sans problèmes de compatibilité
Version minimale pour corriger le bug Lanczos
"""

import os
from PIL import Image

def optimize_images_simple():
    """Version ultra-simple sans Lanczos"""
    
    print("🖼️ === OPTIMISEUR SIMPLE ===")
    
    folder = "data/images"
    target_size = (400, 400)
    quality = 85
    
    if not os.path.exists(folder):
        print(f"❌ Dossier {folder} non trouvé")
        return
    
    # Trouver images
    images = []
    for f in os.listdir(folder):
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            images.append(f)
    
    if not images:
        print("❌ Aucune image trouvée")
        return
    
    print(f"📊 {len(images)} images trouvées")
    print("")
    
    for i, filename in enumerate(images, 1):
        filepath = os.path.join(folder, filename)
        
        try:
            # Taille avant
            size_before = os.path.getsize(filepath)
            print(f"[{i}/{len(images)}] {filename} - {format_size(size_before)}")
            
            # Ouvrir image
            with Image.open(filepath) as img:
                
                # Convertir en RGB si nécessaire
                if img.mode != 'RGB':
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Fond blanc pour transparence
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        if img.mode == 'RGBA':
                            background.paste(img, mask=img.split()[-1])
                            img = background
                    else:
                        img = img.convert('RGB')
                
                # Redimensionner SANS filtre (évite bug Lanczos)
                img_resized = img.resize(target_size)
                
                # Sauvegarder
                base_name = os.path.splitext(filepath)[0]
                output_path = f"{base_name}.jpg"
                
                img_resized.save(
                    output_path,
                    'JPEG',
                    quality=quality,
                    optimize=True
                )
            
            # Taille après
            size_after = os.path.getsize(output_path)
            reduction = ((size_before - size_after) / size_before) * 100
            
            print(f"  ✅ Optimisée: {format_size(size_after)} (-{reduction:.1f}%)")
            
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
    
    print("")
    print("✅ Terminé ! Images optimisées en 400x400px JPEG")

def format_size(bytes):
    """Formate la taille"""
    if bytes < 1024:
        return f"{bytes} B"
    elif bytes < 1024 * 1024:
        return f"{bytes/1024:.1f} Ko"
    else:
        return f"{bytes/(1024*1024):.1f} Mo"

if __name__ == "__main__":
    try:
        optimize_images_simple()
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
    
    input("Appuyez sur Entrée pour fermer...")
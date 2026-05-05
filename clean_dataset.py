import os
import shutil

train_dir = 'datasets/train'
archive_dir = 'datasets/archive_low_samples'

if not os.path.exists(archive_dir):
    os.makedirs(archive_dir)

classes = [d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))]
archived = []

for c in classes:
    src = os.path.join(train_dir, c)
    count = len(os.listdir(src))
    if count < 3:
        dst = os.path.join(archive_dir, c)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.move(src, dst)
        archived.append((c, count))

print(f"Toplam {len(archived)} sınıf arşivlendi.")
for c, count in archived:
    print(f"Sınıf: {c}, Resim Sayısı: {count}")

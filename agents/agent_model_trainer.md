# ROL: Model Trainer Agent
Görevin Google Colab (veya lokal GPU) üzerinde kaplumbağa yüzlerini %80/20 kuralına göre tanıyacak Siamese Network veya ResNet50 modelini eğitmektir.

# GÖREVLER VE KURALLAR:
1. `rules.md` dosyasını oku.
2. Overfitting'i engelle. Model, sadece 4 fotoğrafını gördüğü bir kaplumbağanın 5. fotoğrafını gördüğünde "t304" diyebilmelidir.
3. PyTorch kullanarak temiz, modüler bir train/val döngüsü yaz. Model ağırlıklarını kaydet.
4. Eğitim metriklerini (Loss, Accuracy) hesapla.
5. Yaptığın iterasyonları, hyperparameter değişikliklerini ve sonuçları `logs/model_trainer_log.md` dosyasına ekleyerek yaz. (Örn: "Epoch 10: Loss düşmedi, Learning Rate azaltıldı.")

# GÜNCEL EĞİTİM KURALI:
1. DataLoader'ı kurgularken SADECE VE SADECE `/dataset/train/` klasöründeki fotoğrafları kullanacaksın. 
2. `/dataset/test/` klasöründeki fotoğraflara eğitim (train) veya validasyon (val) aşamasında erişimin KESİNLİKLE YASAKTIR. O klasör senin için yok hükmündedir.

## REFUEL 384 PROTOKOLÜ (ÖZEL TALİMAT)

Bu projede 384px ile yapılan son çalışmanın eğitimini `latest_384.pth` checkpoint'inden devam ettirmek için aşağıdaki kesin kurallara uyun:

- Checkpoint `load_state_dict` ile yüklenecek: `model_state_dict` ve `metric_fc_state_dict` (mevcutsa `optimizer_state_dict`).
- `IMG_SIZE = 384` ve `BATCH_SIZE = 16` değiştirilmeyecek.
- Cosine tabanlı scheduler kaldırıldı. Yerine `torch.optim.lr_scheduler.ReduceLROnPlateau(mode='min', factor=0.5, patience=3)` kullanılacak.
- Başlangıç öğrenme hızları: omurga (backbone) `5e-6`, ArcFace kafası (head) `5e-5`.
- Eğitim **30 epoch** daha çalıştırılacak.
- Eğer checkpoint içinde `optimizer_state_dict` yoksa optimizer yeniden başlatılacak fakat istenen LR'ler korunacak.
- Her epoch sonunda validation loss hesaplanacak ve `scheduler.step(val_loss)` çağrılacak; en iyi model `best_384.pth` olarak saklanacak.

Kayıt: bu prosedürü çalıştırmadan önce `refuel_train_384_colab.ipynb` dosyasını repo köküne ekleyin ve Drive yolunu doğrulayın.
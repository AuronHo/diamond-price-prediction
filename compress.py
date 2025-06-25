import pickle
import gzip

# Step 1: Load the original .pkl file
with open('prediction/diamond_price_predictor_full.pkl', 'rb') as f:
    model = pickle.load(f)

# Step 2: Compress and save the .pkl file using gzip (keeping original file intact)
with gzip.open('prediction/diamond_price_predictor_full_compressed.pkl.gz', 'wb') as f:
    pickle.dump(model, f)

print("File compressed successfully!")

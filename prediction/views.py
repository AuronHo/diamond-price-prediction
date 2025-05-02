from django.shortcuts import render
import joblib
import os

# Get current directory
current_dir = os.path.dirname(__file__)

# Load model package
model_path = os.path.join(current_dir, 'diamond_price_predictor_full.pkl')
package = joblib.load(model_path)

model = package['model']
preprocessor = package['preprocessor']
features_used = package['features']

def home(request):
    return render(request, 'home.html')

def predict_price(request):
    if request.method == 'POST':
        try:
            # Get all form values
            carat = float(request.POST.get('carat'))
            depth = float(request.POST.get('depth'))
            table = float(request.POST.get('table'))
            x = float(request.POST.get('x'))
            y = float(request.POST.get('y'))
            z = float(request.POST.get('z'))
            cut_label = int(request.POST.get('cut_label'))
            clarity_label = int(request.POST.get('clarity_label'))
            color_index = int(request.POST.get('color_index'))

            # One-hot encode color
            color_features = [0] * 7
            color_features[color_index] = 1

            # Final input in the correct order
            final_input = [carat, depth, table, x, y, z] + color_features + [cut_label, clarity_label]

            # Predict
            predicted_price = model.predict([final_input])[0]

            return render(request, 'predict.html', {'predicted_price': round(predicted_price, 2)})

        except Exception as e:
            return render(request, 'predict.html', {'error': f'Something went wrong: {e}'})

    return render(request, 'predict.html')

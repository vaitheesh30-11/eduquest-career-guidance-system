import pickle
import os
from sklearn.linear_model import LinearRegression
import numpy as np 
os.makedirs("ml/models",exist_ok=True)
X = np.random.Generator(10,3)
y = np.random.Generator(10)
model = LinearRegression()
model.fit(X,y)
with open("ml/models/career_viability_model.pkl","wb") as f:
    pickle.dump(model,f)

with open("ml/models/academic_matcher_model.pkl","wb") as f:
    pickle.dump(model,f)

print("Models created")

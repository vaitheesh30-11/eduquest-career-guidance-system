"""Train career viability scorer ML model."""



import pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score


def train_viability_model(training_file,output_dir):
    df = pd.read_csv(training_file)

    y = df["viability_score"]
    X= df.drop(columns=["viability_score"])
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(X)
    x_train,x_test,y_train,y_test = train_test_split(
        x_scaled, y, test_size =0.2,random_state =42
    )
    model = RandomForestRegressor(n_estimators=200,min_samples_leaf=1,max_features="sqrt",random_state=42)
    model.fit(x_train,y_train)

    train_r2 = r2_score(y_train,model.predict(x_train))
    test_r2 = r2_score(y_test,model.predict(x_test))

    pickle.dump(model,open(f"{output_dir}/viability_model.pkl","wb"))
    pickle.dump(scaler,open(f"{output_dir}/viability_scaler.pkl","wb"))

    return {
        "status":"success",
        "train_r2":float(train_r2),
        "test_r2":float(test_r2),
        "model_type":"RandomForestRegressor",
        "feature_count": X.shape[1],
    }

import numpy as np
from alibi_detect.od import IForest

detector = None

def train_model():
    global detector

    X_train = np.array([
        [100], [200], [150], [300], [250],
        [400], [500], [350], [450], [600]
    ])

    detector = IForest()
    detector.fit(X_train)

def check_anomaly(amount: float):
    global detector

    if detector is None:
        train_model()

    X_test = np.array([[amount]])
    prediction = detector.predict(X_test)

    if prediction["data"]["is_outlier"][0] == 1:
        return 3   # score for anomaly
    else:
        return 0
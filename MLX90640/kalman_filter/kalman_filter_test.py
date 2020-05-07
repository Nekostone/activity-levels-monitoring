from kalman_filter_1d import measurement_update, predict

def test_1d_filter():
    print("Testing 1d Kalman Filter...")
    measurements = [5., 6., 7., 9., 10.] # assuming each of this is a computed mean of the measurements taken at specific t
    motion = [1., 1., 2., 1., 1.] # assuming each of this is a computed mean of the change at specific t
    measurement_sig = 4.
    motion_sig = 2.
    mu = 0. # guess first mean value
    sig = 10000. # amount of uncertainty

    for i in range(len(measurements)):
        [mu, sig] = measurement_update(mu, sig, measurements[i], measurement_sig)
        print("measurement update: ", [mu,sig])
        [mu, sig] = predict(mu, sig, motion[i], motion_sig)
        print("predict: ", [mu,sig])
        
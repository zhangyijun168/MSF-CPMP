import lightgbm as lgb
import pandas as pd
from tqdm import tqdm
import pickle
import time
import os

average_epoch_acc = 0

if __name__ == '__main__':
    fd_t = open("./pred_data/LGBM/result_test.txt", "a+")
    for i in tqdm(range(1,11)):
        time.sleep(0.1)
        print('\n')
        epoch_acc = 0
        X_train = pd.read_csv('../../data/data_splitClassifier_235/X_train{}.csv'.format(i))
        y_train = pd.read_csv('../../data/data_splitClassifier_235/y_train{}.csv'.format(i)).to_numpy().reshape(-1)
        test_x = pd.read_csv('../../data/data_splitClassifier_235/X_test{}.csv'.format(i))
        test_y = pd.read_csv('../../data/data_splitClassifier_235/y_test{}.csv'.format(i))
        test_y = test_y['target'].to_numpy()
        numtest = (test_y.shape[0] // 16) * 16
        clf = lgb.LGBMClassifier(objective='binary', learning_rate=0.01,metric='binary_logloss')
        clf.fit(X_train, y_train.astype('int'))
        y_pred = clf.predict_proba(test_x[:numtest])
        y_pred = y_pred[:,1]
        mlist2 = y_pred
        yy = [1 if i >= 0.5 else 0 for i in y_pred]

        epoch_acc += sum(yy == (test_y[:numtest]))
        epoch_acc = (epoch_acc / y_pred.shape[0]) * 100
        average_epoch_acc += epoch_acc
        print(f"epoch: {i},epoch_acc: {epoch_acc:.4f}")

        mlist1 = yy

        t1, t2 = pd.DataFrame(mlist1, columns=['predict']), pd.DataFrame(test_y[:numtest], columns=['true'])
        tt = pd.concat([t1, t2], axis=1)

        os.makedirs(f'./pred_data/LGBM/test1/', exist_ok=True)

        pd.DataFrame(tt).to_csv('./pred_data/LGBM/test1/experiment_{}_predicted_values.csv'.format(i))

        t1, t2 = pd.DataFrame(mlist2, columns=['predict']), pd.DataFrame(test_y[:numtest], columns=['true'])
        tt = pd.concat([t1, t2], axis=1)

        os.makedirs(f'./pred_data/LGBM/test2/', exist_ok=True)

        pd.DataFrame(tt).to_csv('./pred_data/LGBM/test2/experiment_{}_predicted_values.csv'.format(i))

        os.makedirs(f'./pred_model/LGBM_model/', exist_ok=True)
        with open('./pred_model/LGBM_model/{}_LGBM_model_rbf.pkl'.format(i), 'wb') as f:
            pickle.dump(clf, f)

        fd_t.write(f"epoch:{i}, epoch_acc:{epoch_acc:.4f}\n")
    fd_t.write(f"average_epoch_acc: {average_epoch_acc / i:.4f}\n")
    fd_t.close()

    print(f"average_epoch_acc: {average_epoch_acc / i:.4f}")
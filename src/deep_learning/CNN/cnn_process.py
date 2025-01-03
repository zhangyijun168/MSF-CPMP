
import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import scale
import pandas as pd
from torch.nn.utils.rnn import pad_sequence

#  CNN model
class CNN(nn.Module):
    def __init__(self, hidden_size, output_size):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=16, kernel_size=3)
        self.pool1 = nn.AvgPool1d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv1d(in_channels=16, out_channels=32, kernel_size=3)
        self.pool2 = nn.AvgPool1d(kernel_size=2, stride=2)
        self.conv3 = nn.Conv1d(in_channels=32, out_channels=32, kernel_size=3)
        self.pool3 = nn.AvgPool1d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(in_features=32 * 30, out_features=128)
        self.dropout = nn.Dropout(0.2)
        self.fc2 = nn.Linear(in_features=128, out_features=64)
        self.fc3 = nn.Linear(in_features=32, out_features=128)
        self.fc4 = nn.Linear(in_features=32, out_features=256)

        self.nrom = nn.BatchNorm1d(32)
        self.fc = nn.Linear(output_size , hidden_size)
        self.classifier = nn.Linear( 64 , 1)
        self.sig = nn.Sigmoid()
        
    def forward(self, x):
        x = x.unsqueeze(1)
        x = self.conv1(x)
        x = nn.functional.relu(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = nn.functional.relu(x)
        x = self.pool2(x)
        x = x.view(-1, 32 * 30)
        x = self.fc1(x)
        x = self.dropout(x)
        x = nn.functional.relu(x)
        x = self.fc2(x)
        x = self.dropout(x)

        output = self.classifier(x)
        output = self.sig(output)

        output = output.squeeze(1)

        return output


def create_dataset_number(PATH_x,PATH_y):
    df = pd.read_csv(PATH_x)

    df_num = df.drop(columns=['Year', 'CycPeptMPDB_ID', 'Structurally_Unique_ID'
        , 'SMILES', 'Sequence', 'Sequence_LogP', 'Sequence_TPSA', 'Source',
                              'Original_Name_in_Source_Literature', 'HELM',
                              'HELM_URL', 'Molecule_Shape','Permeability','PAMPA']).values  # 自己加的

    df[df['Permeability'] >= -6] = 1
    df[df['Permeability'] < -6] = 0
    y = df['Permeability'].values
    y = y.astype('float32')
    df_num = scale(df_num)
    return df_num,y


def create_dataset_list(PATH_x):
    df_list = pd.read_csv(PATH_x,usecols=['Sequence_LogP','Sequence_TPSA'])
    df_list['Sequence_LogP'] = df_list['Sequence_LogP'].apply(lambda x: eval(x))
    df_list['Sequence_TPSA'] = df_list['Sequence_TPSA'].apply(lambda x: eval(x))
    a = df_list['Sequence_LogP'].values
    b = df_list['Sequence_TPSA'].values

    max_len = max(len(x) for x in a)
    data_padded = np.zeros((len(a), max_len))
    for i, row in enumerate(a):
        data_padded[i, :len(row)] = row

    tensor_data = torch.tensor(data_padded, dtype=torch.float32)
    logp_list = torch.tensor(pad_sequence(tensor_data, batch_first=True, padding_value=0))

    max_len1 = max(len(x) for x in b)
    data_padded = np.zeros((len(b), max_len1))
    for i, row in enumerate(b):
        data_padded[i, :len(row)] = row
    tensor_data = torch.tensor(data_padded, dtype=torch.float32)
    tpsa_list = torch.tensor(pad_sequence(tensor_data, batch_first=True, padding_value=0))

    list_num = torch.cat([logp_list, tpsa_list], dim=1)
    list_num = scale(list_num)
    list_num = torch.tensor(list_num, dtype=torch.float32)
    return list_num


def smi_tokenizer(smi):
    """
    Tokenize a SMILES molecule or reaction
    """
    import re
    pattern = "(\[[^\]]+]|Br?|Cl?|N|O|S|P|F|I|b|c|n|o|s|p|\(|\)|\.|=|#|-|\+|\\\\|\/|:|~|@|\?|>|\*|\$|\%[0-9]{2}|[0-9])"
    regex = re.compile(pattern)
    tokens = [token for token in regex.findall(smi)]
    assert smi == ''.join(tokens)
    return ' '.join(tokens)


def create_dataset_seq(PATH_x):
    df = pd.read_csv(PATH_x,usecols=['SMILES'])
    vocab = []
    datas = []
    for i, row in df.iterrows():
        data = row["SMILES"]
        tokens = smi_tokenizer(data).split(" ")
        if len(tokens) <= 128:
            di = tokens+["PAD"]*(128-len(tokens))
        else:
            di = tokens[:128]
        datas.append(di)
        vocab.extend(tokens)
    vocab = list(set(vocab))
    vocab = ["PAD"]+vocab
    with open("vocab.txt","w",encoding="utf8") as f:
        for i in vocab:
            f.write(i)
            f.write("\n")
    mlist = []
    word2id = {}
    for i,d in enumerate(vocab):
        word2id[d] = i
    for d_i in datas:
        mi = [word2id[d] for d in d_i]
        mlist.append(np.array(mi))
    return mlist


def d_loadar(x1,z):
    X = []
    Z = []
    for x,z in zip(x1,z):
        X.append(x)
        Z.append(z)
        if len(X) == 8:
            o_x = X
            o_z = Z
            X = []
            Z = []

            numpy_array1 = np.array([item.cpu().detach().numpy() for item in o_x])
            numpy_array2 = np.array([item.cpu().detach().numpy() for item in o_z])
            x_res = torch.tensor(numpy_array1)
            z_res = torch.tensor(numpy_array2)

            yield (x_res,z_res)

if __name__ == '__main__':
    t1 = torch.rand(10,2)
    t2 = torch.rand(10,)
    print(t2)

    o_z = []
    for x in t2:
        o_z.append(x)

    print(o_z)

    numpy_array = np.array([item.cpu().detach().numpy() for item in o_z])
    x_res = torch.tensor(numpy_array)

    print(x_res)



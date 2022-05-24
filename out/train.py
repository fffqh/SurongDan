import time
import numpy as np
from torchvision import transforms
from torchvision.datasets import mnist
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import torch.nn as nn
import torch.optim as optim
from torch import Tensor
import torch.nn.functional as F
from model import *
train_batch_size = 128
test_batch_size = 128
transform = transforms.Compose([transforms.ToTensor(),transforms.Normalize([0.5],[0.5])])
data_train = mnist.MNIST('~/data/', train=True, transform=transform,target_transform=None, download=True)
data_test  = mnist.MNIST('~/data/', train=False, transform=transform,target_transform=None, download=True)
train_loader = DataLoader(data_train, batch_size=train_batch_size, shuffle=True)
test_loader = DataLoader(data_test,batch_size=test_batch_size,shuffle=True)
model = myModel()
print(model)
num_epochs = 2
criterion = nn.CrossEntropyLoss()
LR = 0.001
optimizer = optim.Adam(model.parameters(), LR)
train_losses = []
train_acces = []
eval_losses = []
eval_acces = []
print("start training...")
start_time = time.time()
for epoch in range(num_epochs):
	train_loss = 0
	train_acc = 0
	model.train()
	for img, label in train_loader:
		out = model(img)
		loss = criterion(out, label)
		optimizer.zero_grad()
		loss.backward()
		optimizer.step()
		train_loss += loss
		_, pred = out.max(1)
		num_correct = (pred == label).sum().item()
		acc = num_correct / img.shape[0]
		train_acc += acc
	train_losses.append(train_loss / len(train_loader))
	train_acces.append(train_acc / len(train_loader))
	eval_loss = 0
	eval_acc = 0
	model.eval()
	for img, label in test_loader:
		out = model(img)
		loss = criterion(out, label)
		optimizer.zero_grad()
		loss.backward()
		optimizer.step()
		eval_loss += loss
		_, pred = out.max(1)
		num_correct = (pred == label).sum().item()
		acc = num_correct / img.shape[0]
		eval_acc += acc
	eval_losses.append(eval_loss / len(test_loader))
	eval_acces.append(eval_acc / len(test_loader))
	print('epoch:{},Train Loss:{:.4f},Train Acc:{:.4f},Test Loss:{:.4f},Test Acc:{:.4f}'.format(epoch, train_loss / len(train_loader),train_acc / len(train_loader),eval_loss / len(test_loader),eval_acc / len(test_loader)))
	stop_time = time.time()
	print('time is:{:.4f}s'.format(stop_time-start_time))
print('end training.')
plt.figure()
plt.title("loss")
line1,=plt.plot(np.arange(len(train_losses)), train_losses)
line2,=plt.plot(np.arange(len(eval_losses)), eval_losses)
plt.legend(handles=[line1,line2], labels=['train loss','eval loss'])
plt.savefig("./pic/loss.jpg")
plt.figure()
plt.title("acc")
line1,=plt.plot(np.arange(len(train_acces)), train_acces)
line2,=plt.plot(np.arange(len(eval_acces)), eval_acces)
plt.legend(handles=[line1,line2], labels=['train acc','eval acc'])
plt.savefig("./pic/acc.jpg")

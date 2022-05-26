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
class myReshapeLinear(nn.Linear):
	def __init__(self, in_features: int, out_features: int, bias: bool = True, device=None, dtype=None) -> None:
		super(myReshapeLinear, self).__init__(in_features, out_features, bias)
	def forward(self, x: Tensor) -> Tensor:
		x = x.reshape(x.shape[0], -1)
		return F.linear(x, self.weight, self.bias)
class myModel(nn.Module):
	def __init__(self):
		super(myModel, self).__init__()
		self.blocka3=nn.Conv2d(in_channels=1, out_channels=1, kernel_size=3,stride=1, padding=1)
		self.blockb3=nn.ReLU()
		self.blockc3=myReshapeLinear(784, 10)
	def forward(self, x):
		xa3=self.blocka3(x)
		xb3=self.blockb3(xa3)
		xc3=self.blockc3(xb3)
		return xc3

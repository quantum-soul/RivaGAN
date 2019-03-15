import torch
import torch.nn as nn
import torch.nn.functional as F

class Adversary(nn.Module):
    """
    The Adversary module maps a sequence of frames to another sequence of frames
    with a constraint on the maximum distortion of each individual pixel.

    Input: (N, 3, L, H, W)
    Output: (N, 3, L, H, W)
    """

    def __init__(self, l1_max=0.05):
        super(Adversary, self).__init__()
        self.l1_max = l1_max
        self._conv = nn.Sequential(
            nn.Conv3d(3, 32, kernel_size=(1,7,7), padding=(0,3,3), stride=1),
            nn.ELU(),
            nn.InstanceNorm3d(32),
            nn.Conv3d(32, 64, kernel_size=(1,7,7), padding=(0,3,3), stride=(1, 2, 2)),
            nn.ELU(),
            nn.InstanceNorm3d(64),
            nn.ConvTranspose3d(64, 128, kernel_size=(1,7,7), padding=(0,3,3), stride=(1, 2, 2), output_padding=(0, 1, 1)),
            nn.ELU(),
            nn.InstanceNorm3d(128),
            nn.Conv3d(128, 3, kernel_size=(1,1,1), padding=(0,0,0), stride=1),
            nn.Tanh(),
        )

    def forward(self, frames):
        x = frames
        x = self._conv(x)
        return frames + self.l1_max * x
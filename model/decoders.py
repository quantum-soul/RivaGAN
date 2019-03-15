import torch
import torch.nn as nn
import torch.nn.functional as F

class Decoder(nn.Module):
    """
    The Critic module maps a sequence of frames to a fixed-length vector.

    Input: (N, 3, L, H, W)
    Output: (N, D)
    """

    def __init__(self, data_dim):
        super(Decoder, self).__init__()
        self.data_dim = data_dim
        self._conv = nn.Sequential(
            nn.Conv3d(3, 32, kernel_size=(1,11,11)),
            nn.ELU(),
            nn.InstanceNorm3d(32),
            nn.Conv3d(32, 64, kernel_size=(1,11,11), stride=(1, 2, 2)),
            nn.ELU(),
            nn.InstanceNorm3d(64),
            nn.Conv3d(64, 128, kernel_size=(1,11,11)),
            nn.ELU(),
            nn.InstanceNorm3d(128),
        )
        self._pool = nn.MaxPool3d(kernel_size=(1,16,16), stride=(1, 4, 4))
        self._1x1 = nn.Conv3d(256, self.data_dim, kernel_size=(1,1,1))

    def forward(self, frames):
        frames = self._conv(frames)
        frames = torch.cat([self._pool(frames), -self._pool(-frames)], dim=1)
        return torch.mean(self._1x1(frames).view(frames.size(0), self.data_dim, -1), dim=2)
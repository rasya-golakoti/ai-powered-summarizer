# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\config

"""
Configuration for plotting and visualization
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt

@dataclass
class PlotConfig:
    """Plot configuration settings"""
    
    # General settings
    dpi: int = 300
    figsize_wide: Tuple[int, int] = (12, 6)
    figsize_square: Tuple[int, int] = (8, 8)
    figsize_tall: Tuple[int, int] = (8, 10)
    
    # Color palettes
    color_palettes: Dict = None
    
    # Font sizes
    title_fontsize: int = 14
    label_fontsize: int = 12
    tick_fontsize: int = 10
    
    # Style
    style: str = 'seaborn-v0_8-whitegrid'
    grid_alpha: float = 0.3
    
    def __post_init__(self):
        # Define color palettes
        self.color_palettes = {
            'metrics': plt.cm.Blues,
            'emotions': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'],
            'keywords': plt.cm.viridis,
            'speakers': plt.cm.Set2,
            'chapters': plt.cm.tab20c,
        }
    
    def setup_plotting(self):
        """Setup matplotlib configuration"""
        plt.style.use(self.style)
        plt.rcParams['figure.dpi'] = self.dpi
        plt.rcParams['savefig.dpi'] = self.dpi
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = self.grid_alpha
        plt.rcParams['axes.titlesize'] = self.title_fontsize
        plt.rcParams['axes.labelsize'] = self.label_fontsize
        plt.rcParams['xtick.labelsize'] = self.tick_fontsize
        plt.rcParams['ytick.labelsize'] = self.tick_fontsize

# Default configuration
default_config = PlotConfig()
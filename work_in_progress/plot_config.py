import os
os.environ['MPLBACKEND'] = 'Agg'
import matplotlib
matplotlib.use('Agg')  # Must be before importing pyplot
import plotly.io as pio
pio.renderers.default = 'png'  # No display needed

def save_plot(fig, name, folder='work_in_progress'):
    """Save plots without blocking automation"""
    if hasattr(fig, 'savefig'):  # Matplotlib
        fig.savefig(f'{folder}/{name}.png', dpi=150, bbox_inches='tight')
        plt.close(fig)
    else:  # Plotly
        fig.write_image(f'{folder}/{name}.png')
        fig.write_html(f'{folder}/{name}.html')
    print(f"✅ Plot saved: {folder}/{name}.png") 
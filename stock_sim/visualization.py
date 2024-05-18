import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib import gridspec
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

def create_3d_graph(x: list, y: list, z: list, xtitle: str, ytitle: str, ztitle: str, z2: list=None, z2title: str="",
                    tax_ratio: bool=False, check_negative: bool=False) -> None:
    '''
    Creates a heatmap of liquid assets and cash on hand from the results of a 2-variable simulation
    '''
    if z2 is None:
        z2 = []
    fig = plt.figure(figsize = (20,10))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1])

    def millions_formatter(x: float, pos) -> str:
        """Formats axis labels to k or M if the numbers are large enough"""
        if x == 0:
            return "0"
        if np.abs(x) < 1e3:
            return f"{x:.2f}"
        if np.abs(x) < 1e6:
            return f"{x * 1e-3:.2f}k"
        return f"{x * 1e-6:.2f}M"

    def ratio_formatter(x: float, pos) -> str:
        """Foramts axis labels based on the cash-tax ratio"""
        if x == 0.5:
            return "Optimal 2-4x Tax"
        if 0.25 <= x <= 0.75:
            return "Near Optimal 1.5-10x Tax"
        if 0.10 <= x <= 0.90:
            return "Feasible 1.1-50x Tax"
        if 0.05 <= x <= 0.95:
            return "Extreme Boundaries 1-100x Tax"
        if x == -0.1:
            return "Negative Cash Reached"
        return "Not Usable"


    (X, Y) = np.meshgrid(x, y)
    Z = np.array(z)
    Z2 = np.array(z2)

    mesh = ax1.pcolormesh(X, Y, Z, shading='auto', cmap = plt.cm.gist_ncar_r)
    mesh2 = ax2.pcolormesh(X, Y, Z2, shading='auto', cmap = plt.cm.gist_ncar_r) if not tax_ratio\
            else ax2.pcolormesh(X, Y, Z2, shading='auto',
                            cmap = LinearSegmentedColormap.from_list('rg',
                            ["white", "darkred", "gold", "g", "aquamarine", "darkblue"], N=256))

    # Set axis labels
    ax1.set_xlabel(f"{xtitle}", labelpad=20)
    ax1.set_ylabel(f"{ytitle}", labelpad=20)
    ax2.set_xlabel(f"{xtitle}", labelpad=20)
    ax2.set_ylabel(f"{ytitle}", labelpad=20)

    ax1.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    ax2.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

    # Liquid Assets labels
    Z1bounds = [int(min(Z.flatten())),int(max(Z.flatten()))]
    Z1Diff = Z1bounds[1]-Z1bounds[0]
    print(Z1bounds, Z1Diff)
    cbar = fig.colorbar(mesh, ticks=list(range(Z1bounds[0],Z1bounds[1],Z1Diff//20 or 1)))
    cbar.formatter = FuncFormatter(millions_formatter)
    cbar.set_label(f"{ztitle}")

    # Resulting Cash/tax ratio Labels
    tax_ratio_vals = [-0.1, 0, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 1]

    Z2bounds = [min(Z2.flatten()),max(Z2.flatten())]
    Z2Diff = Z2bounds[1]-Z2bounds[0]
    print(Z2bounds, Z2Diff, int(int(Z2bounds[0]*100)), int(Z2bounds[1]*100+1))
    cbar2 = fig.colorbar(mesh2, ticks=tax_ratio_vals if tax_ratio\
                        else list(range(Z2bounds[0],Z2bounds[1],Z2Diff//20 or 1)))
    cbar2.formatter = FuncFormatter(millions_formatter if not tax_ratio else ratio_formatter)
    cbar2.set_label(f"{z2title}")
    cbar.update_ticks()

    # Plot displays
    plt.tight_layout()
    plt.show()

def create_stat_graph(x: list, y: list, ytitle: str) -> None:
    '''
    Creates a box-and-whisker plot/scatter plot from statistical simulation to show %ile ranges
    '''
    fig = plt.figure(figsize = (20,6))

    def millions_formatter_text(x: float) -> str:
        """Formats axis labels to k or M if the numbers are large enough"""
        if x == 0:
            return "0"
        if x < 1e3:
            return f"{x:.2f}"
        if x < 1e6:
            return f"{x * 1e-3:.2f}k"
        return f"{x * 1e-6:.2f}M"

    def millions_formatter(x: float, pos) -> str:
        """Formats axis labels to k or M if the numbers are large enough"""
        if x == 0:
            return "0"
        if x < 1e3:
            return f"{x:.2f}"
        if x < 1e6:
            return f"{x * 1e-3:.2f}k"
        return f"{x * 1e-6:.2f}M"

    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 4])
    ax1 = plt.subplot(gs[0])
    med = np.median(y)
    miny=np.min(y)
    maxy=np.max(y)
    percentile_25 = np.percentile(y, 25)
    percentile_75 = np.percentile(y, 75)
    percentile_5 = np.percentile(y, 5)
    percentile_95 = np.percentile(y, 95)
    errIQR = [[med-percentile_25], [percentile_75-med]]
    err90 = [[med-percentile_5], [percentile_95-med]]

    ax1.errorbar(x=1, y=med, yerr=err90, fmt='o', color='orange',label = '5-95% Percentiles')
    ax1.errorbar(x=1, y=med, yerr=errIQR, fmt='o', color='blue', label = '25-75% Percentiles')
    ax1.scatter(1,miny, color='red', label = 'Min Value')
    ax1.scatter(1,maxy, color='green', label = 'Max Value')
    ax1.text(1.005, miny, f'Min: ${millions_formatter_text(miny)}',
                    verticalalignment='center', color='red')
    ax1.text(1.005, maxy, f'Max: ${millions_formatter_text(maxy)}',
                    verticalalignment='center', color='green')
    ax1.text(1.005, med, f'Median: ${millions_formatter_text(med)}',
                    verticalalignment='center', color='purple')
    ax1.text(1.005, percentile_5, f'5th Percentile: ${millions_formatter_text(percentile_5)}',
                    verticalalignment='center', color='orange')
    ax1.text(1.005, percentile_25, f'25th Percentile: ${millions_formatter_text(percentile_25)}',
                    verticalalignment='center', color='blue')
    ax1.text(1.005, percentile_75, f'75th Percentile: ${millions_formatter_text(percentile_75)}',
                    verticalalignment='center', color='blue')
    ax1.text(1.005, percentile_95, f'95th Percentile: ${millions_formatter_text(percentile_95)}',
                    verticalalignment='center', color='orange')
    ax1.set_ylabel(f"{ytitle}", labelpad=20)
    ax1.set_xticks([])
    ax1.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    ax1.legend()

    ax2 = plt.subplot(gs[1])
    ax2.scatter(x,y,marker='.',s=10)
    # ax2.set_ylabel("Result Assets ($)")
    ax2.set_yticks([])
    ax2.set_xlabel("Simulation Result # ")
    # ax2.set_ylim(bottom=0, top=3 * mean)
    ax2.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

    ax1.grid(color='grey', linestyle='-', linewidth=0.5)
    ax2.grid(color='grey', linestyle='-', linewidth=0.5)
    plt.tight_layout()
    plt.show()

def create_2d_time_graph(x: list, y: list, xtitle: str, ytitle: str, y2: list, y2title: str) -> None:
    '''
    Line graph of liquid assets and cash vs time with resolution of a week from the time simulation
    '''
    fig = plt.figure(figsize = (20,6))

    def millions_formatter_text(x: float) -> str:
        """Formats axis labels to k or M if the numbers are large enough"""
        if x == 0:
            return "0"
        if x < 1e3:
            return f"{x:.2f}"
        if x < 1e6:
            return f"{x * 1e-3:.2f}k"
        return f"{x * 1e-6:.2f}M"

    def millions_formatter(x: float, pos) -> str:
        """Formats axis labels to k or M if the numbers are large enough"""
        if x == 0:
            return "0"
        if x < 1e3:
            return f"{x:.2f}"
        if x < 1e6:
            return f"{x * 1e-3:.2f}k"
        return f"{x * 1e-6:.2f}M"

    def year_formatter(x: float, pos) -> str:
        """Converts week number to year"""
        return f"{x // 52}"

    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1])
    ax1 = plt.subplot(gs[0])
    ax1.plot(x, y, color='black')
    ax1.set_ylabel(f"{ytitle}", labelpad=20)
    ax1.set_xlabel(f"{xtitle}", labelpad= 20)
    ax1.set_xticks([52*n for n in range(len(x)//52+1)])
    ax1.xaxis.set_major_formatter(FuncFormatter(year_formatter))
    ax1.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
    ax1.legend()

    ax2 = plt.subplot(gs[1])
    ax2.plot(x,y2, color='black')
    ax2.set_ylabel(f"{y2title}")
    ax2.set_xlabel(f"{xtitle}", labelpad=20)
    ax2.set_xticks([52*n for n in range(len(x)//52+1)])
    ax2.xaxis.set_major_formatter(FuncFormatter(year_formatter))
    ax2.yaxis.set_major_formatter(FuncFormatter(millions_formatter))

    ax1.grid(color='grey', linestyle='-', linewidth=0.5)
    ax2.grid(color='grey', linestyle='-', linewidth=0.5)
    plt.tight_layout()
    plt.show()

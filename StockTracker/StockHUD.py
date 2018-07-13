import matplotlib.pyplot as plt
import numpy as np
plt.style.use('ggplot')


class StockHUD:

    def __init__(self, Tracker):
        self.tracker = Tracker
        plt.rcParams["axes.grid"] = False
        plt.ion()
        return

    def run_tracker(self):
        opens = self.tracker.get_opens()

        while True:
            currents = self.tracker.get_currents()
            update = self.tracker.generate_block_update(opens, currents)
            self.update_hud(update)

            plt.pause(self.tracker.period)
            print('asdf')

        return

    def update_hud(self, update):

        update = update.astype(float)

        h = 7 * len(update.index) / 9

        if not plt.get_fignums():
            fig, ax = plt.subplots(figsize=(3, h))
            fig.patch.set_facecolor((41. / 255, 75. / 255, 130. / 255))
        else:
            fig = plt.gcf()
            ax = plt.gca()

        v_bound = self.get_vminmax(update)

        im = ax.imshow(np.array(update.iloc[:, :3]),
                       cmap='RdYlGn',
                       interpolation='none',
                       vmin=-v_bound,
                       vmax=v_bound)

        ax.set_xticks(np.arange(3))
        ax.set_yticks(np.arange(len(update.index)))

        x_ticks = ['Today', 'Week', 'Month']
        y_ticks = [a[0] + '\n' + "{0:.2f}".format(a[1])
                   for a in zip(update.index, update['Current'])]

        ax.set_xticklabels(x_ticks, color='white')
        ax.set_yticklabels(y_ticks, color='white')

        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
        for i in range(3):
            for j in range(len(update.index)):
                t = self.get_grid_text(i, j, update)
                text = ax.text(i, j, t, ha='center', va='center', color='black')

        ax.set_title("Stock Live Updates", color='white')
        fig.tight_layout()
        plt.show()
        return

    @staticmethod
    def get_grid_text(x, y, update):
        pct_change = "{0:.2%}".format(update.iloc[y, x] / 100)
        open_price = str(update.iloc[y, x + 4])
        t = pct_change + '\n' + open_price
        return t

    @staticmethod
    def get_vminmax(update):
        max_val = update.iloc[:, :3].max().max()
        min_val = update.iloc[:, :3].min().min()

        if abs(max_val) > abs(min_val):
            return abs(max_val)
        else:
            return abs(min_val)

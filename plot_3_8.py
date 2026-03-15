import matplotlib.pyplot as plt
import math
import os

# ===================== 全局配置 =====================
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
TXT_DIR = "./"  # 待处理txt目录
OUTPUT_IMG_DIR = "./site_distribution_plots"
MAX_INTERVAL = 100  # 最大区间上限


# ===================== 核心函数 =====================
def process_single_file(file_path, save_path):
    """处理单个txt文件，生成纵向柱状图（横纵坐标互换）"""
    # 初始化统计字典：<=1到<=100，all（替代>100）
    interval_stats = {f"<={i}": 0 for i in range(1, MAX_INTERVAL + 1)}
    interval_stats["all"] = 0  # 替换>100为all

    original_sample_sum = 0  # 存储原始样本数总和（正确的总数）
    original_site_nums = []  # 存储原始位点数据
    original_sample_nums = []  # 存储原始样本数数据

    # 1. 读取并解析单个文件数据
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:  # 跳过空行
                    parts = line.split()
                    site_num = int(parts[0])
                    sample_num = float(parts[1])

                    # 累加原始样本数（只算1次，这是正确的总数）
                    original_sample_sum += sample_num
                    original_site_nums.append(site_num)
                    original_sample_nums.append(sample_num)

        # 空数据判断
        if original_sample_sum == 0:
            print(f"⚠️ 文件 {os.path.basename(file_path)} 无有效数据，跳过绘图")
            return

        # 2. 核心累加逻辑（统计每个区间的样本数）
        for site, sample in zip(original_site_nums, original_sample_nums):
            # 所有数据都累加到all区间（确保all是总和）
            interval_stats["all"] += sample
            if site <= MAX_INTERVAL:
                for i in range(site, MAX_INTERVAL + 1):
                    interval_stats[f"<={i}"] += sample

        # 3. 整理有序的区间数据 + 简化X轴标签
        ordered_intervals = [f"<={i}" for i in range(1, MAX_INTERVAL + 1)]
        ordered_intervals.append("all")  # 替换>100为all

        # 提取有数据的区间 + 计算百分比 + 简化标签
        x_labels_original = []  # 原始标签（<=X / all）
        x_labels_simplified = []  # 简化标签（X / all）
        y_values = []  # 原x_values → 现在是y轴数值
        percentages = []

        for interval in ordered_intervals:
            value = interval_stats[interval]
            if value > 0:
                x_labels_original.append(interval)
                # 简化标签逻辑：去掉<=，保留all
                if interval.startswith("<="):
                    simplified_label = interval.replace("<=", "")
                elif interval == "all":
                    simplified_label = "all"
                else:
                    simplified_label = interval
                x_labels_simplified.append(simplified_label)

                y_values.append(value)
                # 计算百分比，all列强制设为100%
                if interval == "all":
                    percent = 100.0  # all列强制100%
                else:
                    percent = (value / original_sample_sum) * 100
                percentages.append(percent)

        # 4. 绘制纵向柱状图（关键：把barh改为bar）
        plt.figure(figsize=(20, 10), dpi=100)  # 宽屏适配X轴多标签
        bars = plt.bar(
            x_labels_simplified,  # X轴：简化后的位点数值（最后一列是all）
            y_values,  # Y轴：样本数总和
            width=0.8,  # 柱子宽度
            color='#2E86AB',
            edgecolor='white',
            alpha=0.8
        )

        # ===== 标签偏移优化（适配纵向柱状图）=====
        label_offset = max(y_values) * 0.01  # 数值标签偏移
        percent_offset = max(y_values) * 0.03  # 百分比标签偏移

        # 添加数值标签 + 百分比标签（显示在柱子上方）
        for idx, bar in enumerate(bars):
            height = bar.get_height()  # 柱子高度（原宽度）
            bar_x = bar.get_x() + bar.get_width() / 2  # 柱子水平中心

            # 1. 数值标签（黑色，加粗）
            plt.text(
                bar_x,
                height + label_offset,
                f"{height:.0f}",
                ha='center', va='bottom',  # 居中、靠下
                fontsize=6, color='#333333',
                weight='bold',
                rotation=0  # 标签水平显示
            )
            # 2. 百分比标签（红色，加粗）
            plt.text(
                bar_x,
                height + percent_offset,
                f"{percentages[idx]:.0f}%",
                ha='center', va='bottom',
                fontsize=6, color='#FF6B6B',
                weight='bold',
                rotation=0
            )

        # 5. 设置图表样式（适配纵向布局）
        file_name = os.path.basename(file_path).replace("_site_sample_distribution.txt", "")
        plt.title(f"{file_name} - 样本携带的位点数区间分布（累加统计）", fontsize=16, pad=20)
        plt.ylabel(f'样本数总和（总样本数：{original_sample_sum:.0f}）', fontsize=12)  # Y轴：样本数
        plt.xlabel('位点数（≤N）/ 总计（all）', fontsize=12)  # X轴：更新标签说明

        # 优化X轴标签显示（旋转45度避免重叠）
        plt.xticks(rotation=45, ha='right', fontsize=7)
        plt.grid(axis='y', alpha=0.3, linestyle='--')  # 网格线改为Y轴

        # 扩展Y轴范围，确保标签显示完整
        plt.ylim(0, max(y_values) * 1.15)
        plt.tight_layout(pad=2)  # 增加内边距

        # 6. 保存图表
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ 已生成图表：{save_path}")

    except ValueError as e:
        print(f"❌ 文件 {os.path.basename(file_path)} 数据格式错误：{e}")
    except Exception as e:
        print(f"❌ 处理文件 {os.path.basename(file_path)} 时出错：{e}")


# ===================== 主程序 =====================
if __name__ == "__main__":
    os.makedirs(OUTPUT_IMG_DIR, exist_ok=True)

    if not os.path.exists(TXT_DIR):
        print(f"❌ 错误：未找到目录 {TXT_DIR}")
        exit(1)

    txt_files = [f for f in os.listdir(TXT_DIR)
                 if f.endswith("_site_sample_distribution.txt") and os.path.isfile(os.path.join(TXT_DIR, f))]

    if not txt_files:
        print(f"⚠️ 未找到 *_site_sample_distribution.txt 文件")
        exit(0)

    print(f"📌 找到 {len(txt_files)} 个待处理文件，开始生成图表...")
    for txt_file in txt_files:
        file_path = os.path.join(TXT_DIR, txt_file)
        img_name = txt_file.replace(".txt", ".png")
        save_path = os.path.join(OUTPUT_IMG_DIR, img_name)
        process_single_file(file_path, save_path)

    print(f"\n🎉 批量处理完成！图表保存至：{OUTPUT_IMG_DIR}")
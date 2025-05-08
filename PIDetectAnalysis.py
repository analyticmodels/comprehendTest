import pandas as pd
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import os

class PIDetectionReportGenerator:
    def __init__(self, PI_result_path):
        self.PI_result_path = PI_result_path
        self.df = self.load_data()
        self.report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.colors = sns.color_palette("viridis", 12).as_hex()

    def load_data(self):
        df = pd.read_csv(self.PI_result_path, header=0)
        df.columns = [col.replace('*', '') if isinstance(col, str) and col.startswith('*') else col for col in df.columns]
        if 'Score' in df.columns:
            df['Score'] = df['Score'].astype(str).str.replace('*', '').astype(float)
        for col in ['BeginOffset', 'EndOffset']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('*', '').astype(int)
        return df

    def summary_stats(self):
        stats = {
            'total_detections': len(self.df),
            'unique_PI_types': self.df['Type'].nunique(),
            'PI_type_counts': self.df['Type'].value_counts().to_dict(),
            'avg_confidence': self.df['Score'].mean(),
            'median_confidence': self.df['Score'].median(),
            'fields_with_PI': self.df['field'].nunique(),
            'rows_with_PI': self.df['row'].nunique(),
            'PI_types_list': self.df['Type'].unique().tolist(),
            'detection_length': (self.df['EndOffset'] - self.df['BeginOffset']).mean()
        }
        stats['confidence_distribution'] = {
            'high_confidence': (self.df['Score'] > 0.9).mean(),
            'medium_confidence': ((self.df['Score'] <= 0.9) & (self.df['Score'] > 0.7)).mean(),
            'low_confidence': (self.df['Score'] <= 0.7).mean()
        }
        stats['avg_score_by_type'] = self.df.groupby('Type')['Score'].mean().to_dict()
        return stats

    def plot_and_save_chart(self, plot_func, filename):
        filepath = os.path.join("charts", filename)
        os.makedirs("charts", exist_ok=True)
        plt.figure(figsize=(8, 5))
        plot_func()
        plt.tight_layout()
        plt.savefig(filepath)
        plt.close()
        filepath="../"+filepath
        return filepath

    def plot_confidence_distribution(self):
        sns.histplot(self.df['Score'], bins=20, kde=True, color=self.colors[0])
        plt.title('Confidence Score Distribution')
        plt.xlabel('Score')
        plt.ylabel('Frequency')

    def plot_PI_type_distribution(self):
        sns.countplot(y='Type', data=self.df, order=self.df['Type'].value_counts().index, hue='Type', palette=self.colors, legend=False)
        plt.title('PI Type Distribution')
        plt.xlabel('Count')
        plt.ylabel('PI Type')

    def generate_markdown_report(self, output_path="reports/PI_detection_report.md"):
        stats = self.summary_stats()
        conf_path = self.plot_and_save_chart(self.plot_confidence_distribution, "confidence_distribution.png")
        PI_path = self.plot_and_save_chart(self.plot_PI_type_distribution, "PI_type_distribution.png")

        md_lines = [
            f"# PI Detection Report",
            f"**Generated:** {self.report_time}\n",
            "## Summary Statistics",
            f"- Total Detections: {stats['total_detections']}",
            f"- Unique PI Types: {stats['unique_PI_types']}",
            f"- Average Confidence: {stats['avg_confidence']:.4f}",
            f"- Median Confidence: {stats['median_confidence']:.4f}",
            f"- Fields with PI: {stats['fields_with_PI']}",
            f"- Rows with PI: {stats['rows_with_PI']}\n",

            "## Confidence Distribution",
            f"- High Confidence (> 0.9): {stats['confidence_distribution']['high_confidence']*100:.1f}%",
            f"- Medium Confidence (0.7 - 0.9): {stats['confidence_distribution']['medium_confidence']*100:.1f}%",
            f"- Low Confidence (<= 0.7): {stats['confidence_distribution']['low_confidence']*100:.1f}%\n",

            "### Confidence Score Distribution Chart",
            f"![Confidence Score Distribution]({conf_path})\n",

            "### PI Type Distribution Chart",
            f"![PI Type Distribution]({PI_path})\n",

            "## Average Confidence by PI Type",
            "| PI Type | Avg Confidence | Count |",
            "|----------|----------------|-------|"
        ]

        for PI_type in stats['PI_types_list']:
            score = stats['avg_score_by_type'][PI_type]
            count = stats['PI_type_counts'].get(PI_type, 0)
            md_lines.append(f"| {PI_type} | {score:.4f} | {count} |")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        print(f"Markdown report generated successfully: {output_path}")
        return output_path

def main():
    generator = PIDetectionReportGenerator("data/detectedPI.csv")
    generator.generate_markdown_report()


if __name__ == "__main__":
    main()

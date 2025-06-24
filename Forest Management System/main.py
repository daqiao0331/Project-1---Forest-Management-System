from project_name.dataset_loader import load_forest_from_files

def main():
    # 从数据目录下的 CSV 文件加载森林图
    forest_graph = load_forest_from_files('data/forest_management_dataset-trees.csv', 'data/forest_management_dataset-paths.csv')
    print(forest_graph)

if __name__ == '__main__':
    main()

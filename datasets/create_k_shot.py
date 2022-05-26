from argparse import ArgumentParser
import os
import pandas as pd

NUM_SPLITS = 5


def k_shot_split(dataset_path, output_path, num_classes, k):
    for i in range(1, NUM_SPLITS+1):
        folder_name = os.path.join(output_path, str(i))
        output_filename = os.path.join(folder_name, "train.csv")
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        symlink_name = os.path.join(folder_name, "test.csv")
        if not os.path.exists(symlink_name):
            # create symlink for test.csv
            os.symlink(os.path.join(os.getcwd(), dataset_path, "test.csv"), symlink_name)

        train_df = pd.read_csv(os.path.join(dataset_path, "train.csv"))
        for j in range(1, num_classes+1):
            train_df_temp = train_df[train_df.iloc[:, 0] == j]
            train_df_temp = train_df_temp.sample(n=k)
            train_df_temp.to_csv(output_filename, header=False, mode="w" if j == 1 else "a", index=False)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--dataset", dest="dataset", type=str, choices=["AG_NEWS", "DBpedia", "SogouNews"], default="AG_NEWS"
    )
    parser.add_argument("--k", dest="k", type=int, default=5)
    args = parser.parse_args()
    num_classes_map = {
        "AG_NEWS": 4,
        "SogouNews": 5,
        "DBpedia": 14,
    }
    num_classes = num_classes_map[args.dataset]
    dataset_path = os.path.join(".local_data", args.dataset)
    output_path = os.path.join(".local_data", args.dataset, f"{args.k}shot")
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    k_shot_split(dataset_path, output_path, num_classes, args.k)

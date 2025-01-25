import os
from math import asin, radians, cos, sqrt, sin
from csv import DictReader, DictWriter

EARTH_RADIUS = 6371000  # in m
DISTANCE_THRESHOLD = 1000  # in m


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat: float = lat2 - lat1
    dlon: float = lon2 - lon1

    sqrt_haversine_alpha: float = sqrt(sin(dlat / 2) ** 2 + (cos(lat1) * cos(lat2) * (sin(dlon / 2) ** 2)))
    distance: float = 2 * EARTH_RADIUS * asin(sqrt_haversine_alpha)

    return distance


class Converter:
    DATA_COLUMN_NAME = "acq_date"
    COVER_TYPE_COLUMN_NAME = "SAMPLE_1"

    def __init__(self, save_directory_path_relative: str) -> None:
        self.save_directory_path: str = os.curdir + save_directory_path_relative
        if not os.path.exists(self.save_directory_path):
            parts = save_directory_path_relative.split("/")
            while "" in parts:
                parts.remove("")
            for end_ind in range(1, len(parts) + 1):
                os.mkdir(os.curdir + "/" + "/".join(parts[:end_ind]))

    def convert_in_directory(self, directory_path: str) -> None:
        files_in_dir: list[str] = os.listdir(directory_path)
        for file_name in files_in_dir:
            if file_name.endswith(".csv"):
                self.convert_single(directory_path + f"/{file_name}")

    def convert_single(self, file_path: str) -> None:
        with open(file=file_path, mode="r", newline="") as f:
            file_data = DictReader(f)
            fields = file_data.fieldnames
            all_data: list[dict[str, str]] = list(file_data)

        all_data.sort(key=lambda row: (row["latitude"], row["longitude"]))
        result_data: list[dict[str, str]] = []  # contains records that will be in result csv
        already_checked: list[dict[str, str]] = []  # contains all checked records (for group checking)

        for row in all_data:
            is_new_fire = True
            for entry in already_checked:
                # calculate distance only if date the same and the types of cover are the same
                if (
                    entry[self.DATA_COLUMN_NAME]
                    == row[self.DATA_COLUMN_NAME]
                    # and entry[self.COVER_TYPE_COLUMN_NAME] == row[self.COVER_TYPE_COLUMN_NAME]
                ):
                    distance = haversine_distance(
                        float(row["latitude"]),
                        float(row["longitude"]),
                        float(entry["latitude"]),
                        float(entry["longitude"]),
                    )

                    if distance <= DISTANCE_THRESHOLD:
                        is_new_fire = False
                        break

            if is_new_fire:
                result_data.append(row)
            already_checked.append(row)

        print(
            f'Було видалено {len(all_data) - len(result_data)} записів для року {file_path.split("/")[-1].split(".")[0]}'
        )
        print("Рік " + file_path.split("/")[-1].split(".")[0] + ", кількість пожеж: " + str(len(result_data)))
        with open(
            self.save_directory_path + "/" + file_path.split("/")[-1].split(".")[0] + "_converted.csv",
            "w+",
            newline="",
        ) as f:
            writer = DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(result_data)


if __name__ == "__main__":
    # print(
    #     "Distance between 2 points is "
    #     + str(haversine_distance(48.219160000000002, 37.628850000000000, 48.223570000000002, 37.585769999999997))
    #     + "m"
    # )
    converter = Converter("/converted")
    converter.convert_in_directory(os.curdir)

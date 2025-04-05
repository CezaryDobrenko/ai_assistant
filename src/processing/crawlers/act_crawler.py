import requests
import logging
import enum
import json


logger = logging.getLogger(__name__)


class ActType(str, enum.Enum):
    USTAWA = "Ustawa"


class ActCrawler:
    url: str
    publisher: str
    file_type: str
    expected_keys: list[str]

    def __init__(
        self,
        url: str = "https://api.sejm.gov.pl/eli/acts/",
        publisher: str = "DU",
        file_type: str = "text.pdf",
    ):
        self.url = url
        self.publisher = publisher
        self.file_type = file_type
        self.expected_keys = ["ELI", "pos"]

    def download(self, year: int, act_type: ActType) -> list[dict]:
        for act in self.list_selected_acts(year=year, act_type=act_type):
            if any([key not in act.keys() for key in self.expected_keys]):
                logger.warning("Invalid act metadata")
                continue

            eli = act["ELI"].replace("/", "_")

            logger.warning(f"Downloading {eli}...")
            content = self.retrieve_file(year=year, position=act["pos"])

            if content is None:
                logger.warning(f"Found empty content")
                continue

            with open(f"processing/output/{eli}.pdf", "wb") as act_pdf:
                act_pdf.write(content)
            with open(f"processing/output/{eli}.json", "w") as file:
                json.dump(act, file, indent=4, ensure_ascii=False)

    def list_selected_acts(self, year: int, act_type: ActType) -> list[dict]:
        selected_acts = []
        for act in self.retrieve_acts_from_year(year):
            if "type" not in act.keys():
                logger.warning("Act type not found")
                continue

            if act["type"] == act_type:
                selected_acts.append(act)

        return selected_acts

    def retrieve_acts_from_year(self, year: int) -> list[dict]:
        try:
            response = requests.get(
                f"{self.url}/{self.publisher}/{year}",
                timeout=10,
            )
            response.raise_for_status()
            listed_acts = response.json().get("items", [])
        except Exception:
            logger.error("Error_during_retrieving_data")
            return []

        return listed_acts

    def retrieve_file(self, year: int, position: int) -> bytes | None:
        try:
            response = requests.get(
                f"{self.url}/{self.publisher}/{year}/{position}/{self.file_type}",
                timeout=10,
            )
            response.raise_for_status()
            output = response.content
        except Exception:
            logger.error("Error_during_retrieving_pdf")
            output = None

        return output

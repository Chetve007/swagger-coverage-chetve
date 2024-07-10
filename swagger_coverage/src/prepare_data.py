import logging

from swagger_coverage.src.models.swagger_data import SwaggerResponse

logger = logging.getLogger("swagger")


def _prepare_swagger(data, status_codes, service, config):
    _ignore_entities(data, service, config)

    res_dict = {}
    for key, value in data.items():
        list_values = list(value.values())
        for values in list_values:
            if 'deprecated' in values:
                if values.get('deprecated'):
                    continue
            res_dict[values.get("operationId")] = []
        for method, description in value.items():
            if 'deprecated' in description:
                if description.get('deprecated'):
                    continue
            res_dict[description.get("operationId")] = {
                "method": method.upper(),
                "description": description.get("description"),
                "path": key,
                "statuses": status_codes,
                "tag": description.get("tags")[0] if "tags" in description else "default",
            }
    return res_dict


def _prepare_openapi(data, status_codes, service, config):
    _ignore_entities(data, service, config)

    res_dict = {}
    uuid = 1
    for key, value in data.items():
        for method, description in value.items():
            if 'deprecated' in description:
                if description.get('deprecated'):
                    continue
            res_dict[uuid] = {
                "method": method.upper(),
                "description": description.get("summary"),
                "path": key,
                "statuses": status_codes,
                "tag": description.get("tags")[0] if "tags" in description else "default",
            }
            uuid = uuid + 1
    return res_dict


def _ignore_entities(data, service, config):
    if not service or not config:
        return None

    if service in config:
        # delete ignore handles
        if config[service]['handles']:
            handles_for_remove = config[service]['handles']
            for handle in handles_for_remove:
                if len(data[handle[1]]) == 1:
                    del data[handle[1]]
                else:
                    del data[handle[1]][handle[0]]

        # delete ignore handles by tag
        if config[service]['tags']:
            tags_for_remove = config[service]['tags']
            ignore_handles_by_tags = []
            for key, value in data.items():
                if 'tags' in list(value.values())[0]:
                    if list(value.values())[0]['tags'][0] in tags_for_remove:
                        ignore_handles_by_tags.append(key)
            for item in ignore_handles_by_tags:
                del data[item]


class PrepareData:
    def prepare_swagger_data(self, data: SwaggerResponse, status_codes: list, service: str, config: dict) -> dict:
        """
        Preparing data for tests
        :param status_codes:
        :param data:
        :param service:
        :param config:
        :return: swagger dict
        """
        type_swagger = data.swagger_type
        return self._map_prepare.get(type_swagger)(data.paths, status_codes, service, config)

    @staticmethod
    def prepare_check_file_data(data: dict) -> dict:
        """
        Prepare data for check
        """
        for k, value in data.items():
            statuses = value.get("statuses")
            if statuses:
                new_statuses = []
                for s in statuses:
                    new_statuses.append({s: 0})
                value["statuses"] = new_statuses
        return data

    _map_prepare = {"swagger": _prepare_swagger, "openapi": _prepare_openapi}

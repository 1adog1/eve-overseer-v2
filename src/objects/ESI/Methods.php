<?php

    namespace Ridley\Objects\ESI;

    class Methods extends Base {

        protected function character_affiliations(array $arguments) {

            return $this->makeRequest(
                endpoint: "/characters/affiliation/",
                url: ($this->esiURL . "latest/characters/affiliation/?datasource=tranquility"),
                method: "POST",
                payload: $arguments["characters"],
                cacheTime: 3600,
                retries: (isset($arguments["retries"]) ? $arguments["retries"] : 0)
            );

        }

        protected function corporation_members(array $arguments) {

            return $this->makeRequest(
                endpoint: "/corporations/{corporation_id}/members/",
                url: ($this->esiURL . "latest/corporations/" . $arguments["corporation_id"] . "/members/?datasource=tranquility"),
                accessToken: $this->accessToken,
                retries: (isset($arguments["retries"]) ? $arguments["retries"] : 0)
            );

        }

        protected function authenticated_search(array $arguments) {

            $categories = implode(",", $arguments["categories"]);
            $search = urlencode($arguments["search"]);
            $language = (isset($arguments["language"]) ? ("&language=" . $arguments["language"]) : "");;
            $strict = (isset($arguments["strict"]) ? ("&strict=" . $arguments["strict"]) : "");

            $url = $this->esiURL . "latest/characters/" . $arguments["character_id"] . "/search/?datasource=tranquility&categories=" . $categories . "&search=" . $search . $language . $strict;

            return $this->makeRequest(
                endpoint: "/characters/{character_id}/search/",
                url: $url,
                accessToken: $this->accessToken,
                retries: (isset($arguments["retries"]) ? $arguments["retries"] : 0)
            );

        }

        protected function universe_names(array $arguments) {

            return $this->makeRequest(
                endpoint: "/universe/names/",
                url: ($this->esiURL . "latest/universe/names/?datasource=tranquility"),
                method: "POST",
                payload: $arguments["ids"],
                cacheTime: 3600,
                retries: (isset($arguments["retries"]) ? $arguments["retries"] : 0)
            );

        }

        protected function character_fleet(array $arguments) {

            return $this->makeRequest(
                endpoint: "/characters/{character_id}/fleet/",
                url: $this->esiURL . "dev/characters/" . $arguments["character_id"] . "/fleet/?datasource=tranquility",
                accessToken: $this->accessToken,
                retries: (isset($arguments["retries"]) ? $arguments["retries"] : 0)
            );

        }

        protected function fleet_wings(array $arguments) {

            return $this->makeRequest(
                endpoint: "/fleets/{fleet_id}/wings/",
                url: $this->esiURL . "latest/fleets/" . $arguments["fleet_id"] . "/wings/?datasource=tranquility",
                accessToken: $this->accessToken,
                retries: (isset($arguments["retries"]) ? $arguments["retries"] : 0)
            );

        }

    }

?>

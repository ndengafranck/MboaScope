// Fixed facts from docs/SCIENCE.md that the page must show. These are not
// results: they describe the data source and never change with a pipeline run.

// IMERG is calibrated to TRMM until May 2014 and to GPM from June 2014
// (docs/SCIENCE.md, "Known threats", item 1). The chart always marks this year.
export const SENSOR_CHANGE_YEAR = 2014

export const REPO_URL = 'https://github.com/yannx8/MboaScope'
export const METHOD_URL = `${REPO_URL}/blob/main/docs/METHOD.md`
export const OSM_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
export const OSM_TILES = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

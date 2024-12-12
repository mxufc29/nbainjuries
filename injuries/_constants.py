from datetime import datetime

# Default http headers
requestheaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/120.0.0.0 Safari/537.36'}
# Report URL stem
urlstem_injreppdf = 'https://ak-static.cms.nba.com/referee/injury/Injury-Report_*.pdf'

# Set the Dimensions for Area and Columns for Extraction, derived from Tabula
# format area params is [top (y1), left(x1), bottom (y1+height), right (x1+width)]
# format column params is [x2_a (first col, second x coordinate), x1_b, x2_b. x1_c, ...]

area_params2223_a = [34.99559288024902, -0.9998814239502193, 566.508092880249, 843.1051185760498]
cols_params2223_a = [83.5684935760498, 157.24349357604981, 230.9184935760498, 360.3759935760498, 483.5184935760498,
                     590.8734935760498]
# use after Injury-Report_2023-05-02_05PM, for rest of the 22-23 season
area_params2223_b = [73.14440731048583, 1.7891566230775788, 530.9547264480591, 841.6342937995912]
cols_params2223_b = [113.34753324050922, 190.17547185440083, 259.6363478614809, 415.39710011978167, 576.4200399543764,
                     658.5101661445619]
area_params2324 = [76.30171985626221, 18.31240634193411, 534.1120389938354, 820.2697929691313]
cols_params2324 = [108.82203265418997, 183.545096237564, 255.11084727516163, 371.93141146888723, 543.4787264560698,
                   655.0371030735015]
area_params2425 = [76.30171985626221, 18.312425612640556, 534.1120389938354, 827.6368748466493]
cols_params2425 = cols_params2324

# key datetimes across relevant seasons
dictkeydts = {'2122': {'regseastart': datetime(2021, 10, 18, 0, 30),
  'regseaend': datetime(2022, 4, 10, 23, 30),
  'ploffstart': datetime(2022, 4, 15, 0, 30),
  'ploffend': datetime(2022, 6, 16, 23, 30),
  'plinstart': datetime(2022, 4, 11, 0, 30),
  'plinend': datetime(2022, 4, 15, 23, 30),
  'asbstart': datetime(2022, 2, 18, 0, 30),
  'asbend': datetime(2022, 2, 22, 23, 30)},
 '2223': {'regseastart': datetime(2022, 10, 17, 0, 30),
  'regseaend': datetime(2023, 4, 9, 23, 30),
  'ploffstart': datetime(2023, 4, 14, 0, 30),
  'ploffend': datetime(2023, 6, 12, 23, 30),
  'plinstart': datetime(2023, 4, 10, 0, 30),
  'plinend': datetime(2023, 4, 14, 23, 30),
  'asbstart': datetime(2023, 2, 17, 0, 30),
  'asbend': datetime(2023, 2, 21, 23, 30)},
 '2324': {'regseastart': datetime(2023, 10, 24, 17, 30),
  'regseaend': datetime(2024, 4, 14, 23, 30),
  'ploffstart': datetime(2024, 4, 19, 0, 30),
  'ploffend': datetime(2024, 6, 17, 23, 30),
  'plinstart': datetime(2024, 4, 15, 0, 30),
  'plinend': datetime(2024, 4, 19, 23, 30),
  'asbstart': datetime(2024, 2, 16, 0, 30),
  'asbend': datetime(2024, 2, 20, 23, 30)},
 '2425': {'regseastart': datetime(2024, 10, 21, 0, 30),
  'regseaend': datetime(1, 1, 1, 0, 0),
  'ploffstart': datetime(1, 1, 1, 0, 0),
  'ploffend': datetime(1, 1, 1, 0, 0),
  'plinstart': datetime(1, 1, 1, 0, 0),
  'plinend': datetime(1, 1, 1, 0, 0),
  'asbstart': datetime(1, 1, 1, 0, 0),
  'asbend': datetime(1, 1, 1, 0, 0)}}

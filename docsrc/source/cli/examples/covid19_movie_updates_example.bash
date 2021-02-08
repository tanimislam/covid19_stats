#!/bin/bash
#SBATCH --nodes=9
#SBATCH --partition=XXXXX
#SBATCH --account=YYYYYY
#SBATCH --time=23:00:00
#SBATCH --job-name="COVID_MOVIE_UPDATES"
#SBATCH --output="COVID_MOVIE_UPDATES.out"
#SBATCH --error="COVID_MOVIE_UPDATES.err"
#SBATCH --comment "just run the problem, see description"

update_date=$(date +"%d-%m-%Y")
#
## first update database
covid19_update_database
#
## now generate the COVID-19 cases and deaths, movies and figures, for regions (MSAs, CONUS, states)
srun -N9 covid19_movie_updates --region nyc bayarea dc richmond nyc losangeles neworleans chicago seattle houston dallas albuquerque newhaven conus --state California Virginia Texas Florida "New York" Pennsylvania Indiana Michigan Hawaii "New Mexico" "New Jersey" Connecticut --topN=50 --dirname=docs --info

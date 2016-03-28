# TsDemux

This docker application batch-demuxes transport streams from PVR programs like [VDR](http://www.tvdr.de/) or [tvheadend](https://tvheadend.org/) by processing them with [Project X](http://project-x.sourceforge.net/).


## How it works

Parses or waits (watch mode) for a demux jobfile in JSON format and processes every entry with Project X.

The output files receive an individual title, the recoding timestamp and, if language meta-data is available, the language code so you can tell better which audio tracks to keep.
Right after the job file was read it will be renamed so it can not be processed again (by mistake or in watch mode, see below).


## Usage

The application knows two modes

 * single: container will process one job file and exit then
 * continuous watch mode: container will continously watch for a job file, process it and watch again until the container is stopped

To be able to process the files the directory in which they are in has to be mounted in the container, e.g. in /mnt/pvr.

    docker run|start -v /dirToTsFiles:/mnt/pvr oniekrenz/docker-tsdemux /mnt/pvr/demuxjob.json

**Nota Bene**: If you are using a docker-machine on Windows or Mac OS make sure the working directory is located within a shared folder of the host VM. By default only your home directory is automatically shared.


### Single mode

Just pass the jobfile as the first parameter to the container. You might add the `--test` option to test the jobfile syntax and see what would be executed.

    docker run [--rm] ... oniekrenz/docker-tsdemux [--test] jobfile

### Watch mode

Pass the `--watch` option to go into continuous watch mode. Useful when the container was started as a daemon.

    docker run -d ... oniekrenz/docker-tsdemux --watch jobfile


## Example

Given this directory structure

    /somedir
    +- /Misery
    |  +- /2016-03-13.01.05.99.99.rec
    |     +- 001.vdr
    |     +- 002.vdr
    |     +- 003.vdr
    |     +- index.vdr
    |     +- info.vdr
    +- /Spider-Man
    |  +- Spider-Man.2016-03-19.19-15.ts
    +- demuxjob.json   
         
and the demuxjob.json containing
    
    {
        "entries": [
            {
                "dir": "Misery",
                "title": "Misery (1990)"
            },
            {
                "dir": "Spider-Man",
                "title": "Spider-Man (2002)"
            }
        ]
    }

you would then start the demuxing with this command

    docker run --rm -v /somedir:/mnt/pvr oniekrenz/docker-tsdemux /mnt/pvr/demuxjob.json

and, after a few minutes, get these additional files like these

    /somedir
    +- Misery (1990)_2016-03-13_01-05_log.txt
    +- Misery (1990)_2016-03-13_01-05-02.mp2
    +- Misery (1990)_2016-03-13_01-05.ac3
    +- Misery (1990)_2016-03-13_01-05.m2v
    +- Misery (1990)_2016-03-13_01-05.m2v.info
    +- Misery (1990)_2016-03-13_01-05.mp2
    +- Misery (1990)_2016-03-13_01-05.sup
    +- Misery (1990)_2016-03-13_01-05.sup.IFO
    +- Spider-Man (2002)_2016-03-19_19-15 ger.ac3
    +- Spider-Man (2002)_2016-03-19_19-15 ger.mp2
    +- Spider-Man (2002)_2016-03-19_19-15_log.txt
    +- Spider-Man (2002)_2016-03-19_19-15-02 mul.mp2
    +- Spider-Man (2002)_2016-03-19_19-15.m2v
    +- Spider-Man (2002)_2016-03-19_19-15.m2v.info

Notice the additional language tags like 'ger' (= German) or 'mul' (multi-purpose?) in the Spider-Man files.  
You may now open them in programs like [Cuttermaran](http://www.cuttermaran.de/) to cut away the advertisements.

Enjoy


# ToDo

* 
* Implement 'Exclude directories' feature
* Pipe stdout to log file
* Catch errors
* Do not rename to '_done' during processing

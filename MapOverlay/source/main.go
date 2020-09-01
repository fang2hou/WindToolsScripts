package main

import (
	"encoding/csv"
	"fmt"
	"io"
	"log"
	"os"
	"sort"
	"strconv"
)

type overlay struct {
	ID                int
	UIMapArtID        int
	TextureWidth      int
	TextureHeight     int
	OffsetX           int
	OffsetY           int
	HitRectTop        int
	HitRectBottom     int
	HitRectLeft       int
	HitRectRight      int
	PlayerConditionID int
	Flags             int
	AreaID            [4]int
}

type overlayTile struct {
	ID                int
	RowIndex          int
	ColIndex          int
	LayerIndex        int
	FileDataID        int
	WorldMapOverlayID int
}

func main() {
	overlaysFileName := "worldmapoverlay.csv"
	overlayTilesFileName := "worldmapoverlaytile.csv"

	overlays := loadOverlay(overlaysFileName)
	overlayTiles := loadOverlayTiles(overlayTilesFileName)

	mapTexture := make(map[int]map[string][]int)

	for _, overlayTile := range overlayTiles {
		worldMapOverlayID := overlayTile.WorldMapOverlayID
		overlay := overlays[worldMapOverlayID]

		textureInfo := fmt.Sprintf("%d:%d:%d:%d",
			overlay.TextureWidth,
			overlay.TextureHeight,
			overlay.OffsetX,
			overlay.OffsetY)

		thisMap := mapTexture[overlay.UIMapArtID]

		if thisMap == nil {
			thisMap = make(map[string][]int)
		}

		if thisMap[textureInfo] == nil {
			thisMap[textureInfo] = []int{overlayTile.FileDataID}
		} else {
			alreadyExist := false
			for _, dataID := range thisMap[textureInfo] {
				if dataID == overlayTile.FileDataID {
					alreadyExist = true
				}
			}

			if !alreadyExist {
				thisMap[textureInfo] = append(thisMap[textureInfo], overlayTile.FileDataID)
			}
		}

		mapTexture[overlay.UIMapArtID] = thisMap
	}

	exportData("data.lua", mapTexture)
}

func toInt(text string) int {
	number, err := strconv.Atoi(text)
	if err != nil {
		log.Fatalln("The text cannot be converted to int", err)
	}
	return number
}

func loadOverlay(filePath string) map[int]overlay {
	csvfile, err := os.Open(filePath)
	if err != nil {
		log.Fatalln("Couldn't open the csv file", err)
	}
	defer csvfile.Close()

	csvReader := csv.NewReader(csvfile)

	overlays := make(map[int]overlay)

	// Skip the first line
	csvReader.Read()

	for {
		row, err := csvReader.Read()
		if err != nil && err != io.EOF {
			log.Fatalf("can not read, err is %+v", err)
		}
		if err == io.EOF {
			break
		}

		overlays[toInt(row[0])] = overlay{
			ID:                toInt(row[0]),
			UIMapArtID:        toInt(row[1]),
			TextureWidth:      toInt(row[2]),
			TextureHeight:     toInt(row[3]),
			OffsetX:           toInt(row[4]),
			OffsetY:           toInt(row[5]),
			HitRectTop:        toInt(row[6]),
			HitRectBottom:     toInt(row[7]),
			HitRectLeft:       toInt(row[8]),
			HitRectRight:      toInt(row[9]),
			PlayerConditionID: toInt(row[10]),
			Flags:             toInt(row[11]),
			AreaID: [4]int{
				toInt(row[12]),
				toInt(row[13]),
				toInt(row[14]),
				toInt(row[15]),
			},
		}
	}

	return overlays
}

func loadOverlayTiles(filePath string) map[int]overlayTile {
	csvfile, err := os.Open(filePath)
	if err != nil {
		log.Fatalln("Couldn't open the csv file", err)
	}
	defer csvfile.Close()

	csvReader := csv.NewReader(csvfile)

	overlayTiles := make(map[int]overlayTile)

	// Skip the first line
	csvReader.Read()

	for {
		row, err := csvReader.Read()
		if err != nil && err != io.EOF {
			log.Fatalf("can not read, err is %+v", err)
		}
		if err == io.EOF {
			break
		}

		overlayTiles[toInt(row[0])] = overlayTile{
			ID:                toInt(row[0]),
			RowIndex:          toInt(row[1]),
			ColIndex:          toInt(row[2]),
			LayerIndex:        toInt(row[3]),
			FileDataID:        toInt(row[4]),
			WorldMapOverlayID: toInt(row[5]),
		}
	}

	return overlayTiles
}

func exportData(filePath string, data map[int]map[string][]int) {
	os.Remove(filePath)
	file, err := os.Create(filePath)
	if err != nil {
		log.Fatalln("Couldn't open the result file.", err)
	}
	defer file.Close()

	var idList []int
	for id := range data {
		idList = append(idList, id)
	}
	sort.Ints(idList)

	fmt.Fprintln(file, "local RevealDatabase = {")

	for _, id := range idList {
		fmt.Fprintln(file, "    ["+strconv.Itoa(id)+"] = {")

		var mapInfoList []string
		for mapInfo := range data[id] {
			mapInfoList = append(mapInfoList, mapInfo)
		}
		sort.Strings(mapInfoList)

		for _, mapInfo := range mapInfoList {
			dataIDs := data[id][mapInfo]
			sort.Ints(dataIDs)
			fmt.Fprintf(file, "        [\"%s\"] = \"", mapInfo)
			for index, dataID := range dataIDs {
				if index == 0 {
					fmt.Fprintf(file, "%d", dataID)
				} else {
					fmt.Fprintf(file, ", %d", dataID)
				}

			}
			fmt.Fprintf(file, "\",\n")
		}

		fmt.Fprintln(file, "    },")
	}

	fmt.Fprintln(file, "}")
}

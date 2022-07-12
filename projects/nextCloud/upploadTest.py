import nextcloud_client
import os

nc = nextcloud_client.Client('https://cloud.quorum.sk')
nc.login('dano', 'Danger43849')
toDirName = 'testdir'
toFileName = 'test.txt'
fromDirName = "h:\\"
fromFileName = toFileName
nc.mkdir(toDirName)

nc.put_file(os.path.join(toDirName, toFileName), os.path.join(fromDirName, fromFileName))

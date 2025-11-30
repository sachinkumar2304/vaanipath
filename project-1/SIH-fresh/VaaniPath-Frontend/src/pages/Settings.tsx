import { LanguageSwitcher } from '@/components/LanguageSwitcher';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";

export const Settings = () => {
    const { t } = useTranslation();

    return (
        <div className="container mx-auto py-8 px-4">
            <h1 className="text-3xl font-bold mb-8">{t('common.settings')}</h1>

            <div className="grid gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>{t('common.language')}</CardTitle>
                        <CardDescription>{t('common.selectLanguage')}</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex flex-col space-y-2">
                                <Label>{t('common.language')}</Label>
                                <LanguageSwitcher variant="list" />
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};
